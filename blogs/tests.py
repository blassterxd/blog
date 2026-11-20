from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import BlogPost


class BlogTests(TestCase):
    def setUp(self):
        self.a = User.objects.create_user('alice', password='pass12345')
        self.b = User.objects.create_user('bob', password='pass12345')

    def make(self, title='Пост', owner=None):
        return BlogPost.objects.create(
            title=title, text='Текст', owner=owner or self.a
        )

    def test_order_newest_first(self):
        """Новые публикации идут первыми."""
        now = timezone.now()
        for n in range(3):
            p = self.make('пост%d' % n)
            BlogPost.objects.filter(id=p.id).update(
                date_added=now + timedelta(minutes=n)
            )
        r = self.client.get(reverse('blogs:index'))
        t = [p.title for p in r.context['posts']]
        self.assertEqual(t, ['пост2', 'пост1', 'пост0'])

    def test_empty_state(self):
        """Пустой блог показывает сообщение."""
        r = self.client.get(reverse('blogs:index'))
        self.assertContains(r, 'Публикаций пока нет')

    def test_read_without_login(self):
        """Читать можно без входа, кнопки создания нет."""
        self.make('Открытая запись')
        r = self.client.get(reverse('blogs:index'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Открытая запись')
        self.assertNotContains(r, 'Новая публикация')

    def test_create_requires_login(self):
        """Без входа создать нельзя."""
        u = reverse('blogs:create')
        r = self.client.get(u)
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse('users:login'), r.url)
        r = self.client.post(u, {'title': 'X', 'text': 'Y'})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(BlogPost.objects.count(), 0)

    def test_owner_is_set_automatically(self):
        """Автор берётся из request.user, а не из формы."""
        self.client.force_login(self.b)
        r = self.client.post(reverse('blogs:create'), {
            'title': 'Новая',
            'text': 'Текст',
            'owner': self.a.id,
        })
        self.assertEqual(r.status_code, 302)
        p = BlogPost.objects.get(title='Новая')
        self.assertEqual(p.owner, self.b)

    def test_author_can_edit(self):
        """Автор редактирует свою запись."""
        p = self.make('Старое')
        self.client.force_login(self.a)
        r = self.client.post(reverse('blogs:edit', args=[p.id]), {
            'title': 'Новое',
            'text': 'Другой текст',
        })
        self.assertEqual(r.status_code, 302)
        p.refresh_from_db()
        self.assertEqual(p.title, 'Новое')

    def test_cannot_change_owner_by_post(self):
        """Ручной POST не меняет автора."""
        p = self.make()
        self.client.force_login(self.a)
        self.client.post(reverse('blogs:edit', args=[p.id]), {
            'title': 'Т',
            'text': 'Т',
            'owner': self.b.id,
        })
        p.refresh_from_db()
        self.assertEqual(p.owner, self.a)

    def test_foreign_edit_gives_404(self):
        """Чужую запись открыть и изменить нельзя."""
        p = self.make('Чужая')
        self.client.force_login(self.b)
        u = reverse('blogs:edit', args=[p.id])
        self.assertEqual(self.client.get(u).status_code, 404)
        r = self.client.post(u, {'title': 'Взлом', 'text': 'Взлом'})
        self.assertEqual(r.status_code, 404)
        p.refresh_from_db()
        self.assertEqual(p.title, 'Чужая')

    def test_missing_id_gives_404(self):
        """Несуществующий id даёт 404, а не 500."""
        self.client.force_login(self.a)
        r = self.client.get(reverse('blogs:edit', args=[9999]))
        self.assertEqual(r.status_code, 404)

    def test_edit_link_only_for_author(self):
        """Ссылка редактирования видна только автору."""
        p = self.make()
        u = reverse('blogs:edit', args=[p.id])
        self.client.force_login(self.a)
        self.assertContains(self.client.get(reverse('blogs:index')), u)
        self.client.force_login(self.b)
        self.assertNotContains(self.client.get(reverse('blogs:index')), u)

    def test_registration_logs_in(self):
        """После регистрации пользователь сразу вошёл."""
        r = self.client.post(reverse('users:register'), {
            'username': 'carol',
            'password1': 'Str0ng-pass-2026',
            'password2': 'Str0ng-pass-2026',
        })
        self.assertEqual(r.status_code, 302)
        self.assertTrue(User.objects.filter(username='carol').exists())
        self.assertIn('_auth_user_id', self.client.session)

    def test_logout_only_by_post(self):
        """Выход возможен только методом POST."""
        self.client.force_login(self.a)
        r = self.client.get(reverse('users:logout'))
        self.assertEqual(r.status_code, 405)
        self.assertIn('_auth_user_id', self.client.session)
        r = self.client.post(reverse('users:logout'))
        self.assertEqual(r.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)