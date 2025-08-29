
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plagiarismchecker', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DatasetDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dataset_name', models.CharField(db_index=True, default='default', max_length=100)),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField(blank=True, null=True)),
                ('source_file', models.FileField(blank=True, null=True, upload_to='dataset_docs/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='TrainedDatasetModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dataset_name', models.CharField(max_length=100, unique=True)),
                ('vectorizer_path', models.CharField(max_length=500)),
                ('matrix_path', models.CharField(max_length=500)),
                ('doc_index_path', models.CharField(max_length=500)),
                ('trained_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
