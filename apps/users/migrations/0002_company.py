from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=200, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='CompanyMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(blank=True, default='member', max_length=50)),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='memberships', to='users.company')),
                ('user', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='company_memberships', to='users.user')),
            ],
            options={
                'ordering': ['company__name'],
                'unique_together': {('user', 'company')},
            },
        ),
        migrations.AddField(
            model_name='user',
            name='companies',
            field=models.ManyToManyField(blank=True, through='users.CompanyMembership', to='users.Company', related_name='users'),
        ),
    ]
