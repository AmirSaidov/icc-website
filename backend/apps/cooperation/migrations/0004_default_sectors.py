"""
Сферы презентаций по умолчанию — «Промышленность» и «Информационные технологии» (ru / en / zh).
Сотрудники добавляют новые в админке. Slug — те же, что сгенерировало бы автозаполнение.
"""
from django.db import migrations

SECTORS = [
    {
        "name": ("Промышленность", "Industry", "工业"),
        "slug": ("promyshlennost", "industry", "gong-ye"),
    },
    {
        "name": ("Информационные технологии", "Information technology", "信息技术"),
        "slug": ("informatsionnye-tekhnologii", "information-technology", "xin-xi-ji-shu"),
    },
]

LANGS = ("ru", "en", "zh")


def create_sectors(apps, schema_editor):
    Sector = apps.get_model("cooperation", "Sector")
    for order, sector in enumerate(SECTORS):
        if Sector.objects.filter(slug_ru=sector["slug"][0]).exists():
            continue
        fields = {"order": order, "name": sector["name"][0], "slug": sector["slug"][0]}
        for index, lang in enumerate(LANGS):
            fields[f"name_{lang}"] = sector["name"][index]
            fields[f"slug_{lang}"] = sector["slug"][index]
        Sector.objects.create(**fields)


def delete_sectors(apps, schema_editor):
    Sector = apps.get_model("cooperation", "Sector")
    Sector.objects.filter(slug_ru__in=[s["slug"][0] for s in SECTORS], presentations__isnull=True).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("cooperation", "0003_sector_presentation"),
    ]

    operations = [
        migrations.RunPython(create_sectors, delete_sectors),
    ]
