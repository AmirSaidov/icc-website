# Приёмка MVP бэкенда

Сводка по разделам 6 и 8 SPEC.md. Все пути — относительно `backend/`. Весь набор: `pytest` (на момент приёмки — 163 теста, все зелёные).

## Раздел 6: тесты критериев

| # | Критерий | Тест(ы) | Статус |
|---|---|---|---|
| 1 | Новость с тремя переводами, фото и PDF появляется в `/news/?lang=zh` с галереей и вложением | `apps/news/tests/test_api.py::test_news_with_three_translations_photo_and_pdf_is_visible_in_zh`; полностью через форму админки под Редактором — `apps/news/tests/test_admin.py::test_editor_creates_news_with_photo_and_pdf_and_it_is_in_zh_api` | ✅ |
| 2 | Редактор: 403/скрытие для пользователей, групп, ContactInfo, SiteSettings; не может удалить обращение и менять в нём что-то кроме `status` / `admin_note` | `apps/core/tests/test_admin.py::test_all_admin_pages_open[editor]`, `::test_editor_index_hides_restricted_sections`; `apps/feedback/tests/test_admin.py::test_editor_can_change_only_status_and_admin_note`, `::test_editor_cannot_delete` | ✅ |
| 3 | Запись без zh: нет в списке `?lang=zh`, детальный ответ — 200, `is_translated: false`, `null` в переводимых полях | `apps/news/tests/test_api.py::test_untranslated_record_absent_in_zh_list_but_detail_returns_nulls` | ✅ |
| 4 | Детальный ответ находит запись по slug на другом языке | `apps/news/tests/test_api.py::test_detail_found_by_slug_in_any_language` (ru / en / zh) | ✅ |
| 5 | `POST /feedback/` с пустым email → 400 с ошибкой по полю `email` | `apps/feedback/tests/test_api.py::test_empty_email_returns_400_with_field_error` | ✅ |
| 6 | Шестой `POST /feedback/` за час с одного IP → 429 | `apps/feedback/tests/test_api.py::test_sixth_request_per_hour_returns_429` | ✅ |
| 7 | Honeypot: заполненное `website` → 201, в БД записи нет | `apps/feedback/tests/test_api.py::test_honeypot_returns_201_but_saves_nothing` | ✅ |
| 8 | Успешное обращение сохраняется и отправляет письмо (`mail.outbox`) | `apps/feedback/tests/test_api.py::test_valid_feedback_is_saved_and_emailed` | ✅ |
| 9 | Ошибка SMTP не ломает сохранение | `apps/feedback/tests/test_api.py::test_smtp_error_does_not_break_saving` | ✅ |
| 10 | `/events/?when=upcoming` и `?when=past` правильно делят и сортируют | `apps/news/tests/test_api.py::test_events_when_upcoming_and_past_split_and_sort` | ✅ |
| 11 | Черновики (`draft`, `review`) не видны в API | `apps/news/tests/test_api.py::test_drafts_and_review_are_hidden[draft/review]`; также `apps/pages/tests/test_api.py::test_drafts_hidden_in_directions_and_services`, `apps/core/tests/test_seo.py::test_drafts_not_in_sitemap` | ✅ |
| 12 | Партнёр без `consent_to_publish` не виден в API | `apps/cooperation/tests/test_api.py::test_partner_without_consent_is_hidden` | ✅ |
| 13 | `/sitemap.xml` содержит hreflang; `/robots.txt` закрывает `/api/` и не раскрывает путь админки (её закрывает `X-Robots-Tag`) | `apps/core/tests/test_seo.py::test_sitemap_has_hreflang_alternates_and_robots_closes_api`, `::test_robots_does_not_reveal_admin_url`, `::test_admin_responses_have_x_robots_tag` | ✅ |
| 14 | HTML с `<script>` в `content` вырезается при сохранении | `apps/news/tests/test_admin.py::test_script_is_removed_on_save`; разметка CKEditor проходит без поломок — `::test_ckeditor_markup_survives_sanitizer` | ✅ |

Запуск только этих тестов:

```
pytest apps/news/tests/test_api.py::test_news_with_three_translations_photo_and_pdf_is_visible_in_zh apps/news/tests/test_admin.py::test_editor_creates_news_with_photo_and_pdf_and_it_is_in_zh_api apps/core/tests/test_admin.py::test_all_admin_pages_open apps/core/tests/test_admin.py::test_editor_index_hides_restricted_sections apps/feedback/tests/test_admin.py::test_editor_can_change_only_status_and_admin_note apps/feedback/tests/test_admin.py::test_editor_cannot_delete apps/news/tests/test_api.py::test_untranslated_record_absent_in_zh_list_but_detail_returns_nulls apps/news/tests/test_api.py::test_detail_found_by_slug_in_any_language apps/feedback/tests/test_api.py::test_empty_email_returns_400_with_field_error apps/feedback/tests/test_api.py::test_sixth_request_per_hour_returns_429 apps/feedback/tests/test_api.py::test_honeypot_returns_201_but_saves_nothing apps/feedback/tests/test_api.py::test_valid_feedback_is_saved_and_emailed apps/feedback/tests/test_api.py::test_smtp_error_does_not_break_saving apps/news/tests/test_api.py::test_events_when_upcoming_and_past_split_and_sort apps/news/tests/test_api.py::test_drafts_and_review_are_hidden apps/cooperation/tests/test_api.py::test_partner_without_consent_is_hidden apps/core/tests/test_seo.py::test_sitemap_has_hreflang_alternates_and_robots_closes_api apps/news/tests/test_admin.py::test_script_is_removed_on_save
```

## Раздел 8: критерии приёмки MVP

| # | Критерий | Как проверено | Результат |
|---|---|---|---|
| 1 | Проект поднимается по README на чистой машине | Клон ветки `backend-mvp` с GitHub во временную папку, новый venv, команды из `README.md` дословно (cmd), затем `check`, `pytest`, запросы к API и админке на `runserver` | ✅ (подробности ниже) |
| 2 | Редактор создаёт новость на трёх языках с фото и PDF, и она сразу есть в `/api/v1/news/?lang=zh` | Автотест через форму админки под Редактором (тест 1). Вручную на этапе 3: вход под `editor` через форму логина, создание новости с фото и PDF через админку, проверка `/api/v1/news/?lang=zh` на живом `runserver` (галерея WebP и PDF отдаются) | ✅ |
| 3 | Редактор не видит пользователей, контактную информацию и системные настройки | Автотесты (тест 2): разделов нет на главной админки, прямые адреса — 403. Вручную — скриншот админки под `editor` (этап 3) | ✅ |
| 4 | Запись без китайского перевода не ломает API: детальный ответ отдаёт `is_translated: false` | Автотест (тест 3). В seed-данных — 2 записи без zh; реальный пример ответа — в `docs/API.md` («Новость без перевода на zh») | ✅ |
| 5 | Форма с пустым email → 400 с ошибкой по полю; шестой запрос за час → 429 | Автотесты (тесты 5, 6). Вручную на живом `runserver` (этап 4): 400 `{"email": [...]}`, шестой запрос — 429 с `Retry-After` | ✅ |
| 6 | Новое обращение видно в админке и приходит на почту | Автотест (тест 8). Вручную (этап 4): обращение через `curl` → видно в админке, письмо с темой, полями и ссылкой на админку — в консоли (console backend). Реальный SMTP не проверялся: его ещё нет (раздел 9) | ✅ (почта — console backend) |

### Критерий 1: проверка с чистой машины

17.10.2026, Windows 11, Python 3.12.10:

1. `git clone -b backend-mvp https://github.com/AmirSaidov/icc-website.git` — во временную папку вне рабочей копии.
2. Команды из `README.md` (вариант cmd) — дословно, по порядку. `pip` без кэша (`PIP_NO_CACHE_DIR=1`), все пакеты скачаны заново. Время — около 2 мин 40 с.
   - `pip install` — все версии из `requirements.txt`;
   - `migrate` — 44 миграции без ошибок; `createcachetable` — без ошибок;
   - `seed` — созданы все данные раздела 5.4 и пользователи `admin` / `editor`, пароли выведены в консоль;
   - `python` в PATH — из нового `.venv`.
3. `runserver`:
   - `/api/v1/home/?lang=zh`, `/api/v1/news/?lang=en`, `/api/v1/contacts/?lang=zh`, `/api/docs/`, `/api/schema/`, `/admin/login/`, `/sitemap.xml`, `/robots.txt` — 200;
   - превью обложки — 200, `image/webp`;
   - вход в админку под `admin` с паролем из `seed` — успешно, главная админки — 200;
   - `POST /api/v1/feedback/` — 201.
4. В клоне: `python manage.py check` — без ошибок, `pytest` — 163 passed; `git status` после всех команд пуст (`db.sqlite3`, `.env`, `media/`, `logs/`, `.venv/` в git не попадают).

Результат: проект поднимается по README без правок.
