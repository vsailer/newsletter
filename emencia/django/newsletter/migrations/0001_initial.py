# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-01-28 09:57
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion
import emencia.django.newsletter.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('file_attachment', models.FileField(upload_to=emencia.django.newsletter.models.get_newsletter_storage_path, verbose_name='file to attach')),
            ],
            options={
                'verbose_name': 'attachment',
                'verbose_name_plural': 'attachments',
            },
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email')),
                ('title', models.CharField(blank=True, max_length=255, verbose_name='Bezeichnung')),
                ('degree', models.CharField(blank=True, max_length=50, verbose_name='Titel')),
                ('company', models.CharField(blank=True, max_length=255, verbose_name='Firma')),
                ('salutation', models.CharField(blank=True, max_length=50, verbose_name='Anrede')),
                ('first_name', models.CharField(blank=True, max_length=100, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=100, verbose_name='last name')),
                ('subscriber', models.BooleanField(default=True, verbose_name='subscriber')),
                ('valid', models.BooleanField(default=True, verbose_name='valid email')),
                ('tester', models.BooleanField(default=False, verbose_name='contact tester')),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='creation date')),
                ('modification_date', models.DateTimeField(auto_now=True, verbose_name='modification date')),
                ('activation_date', models.DateTimeField(blank=True, null=True, verbose_name='Bestätigungsdatum')),
                ('import_id', models.CharField(blank=True, editable=False, max_length=255, null=True, verbose_name='ImportID')),
                ('source', models.CharField(default='web', max_length=20, verbose_name='Quelle')),
                ('syncing', models.BooleanField(default=False, editable=False, verbose_name='wird synchronisiert')),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'contact',
                'verbose_name_plural': 'contacts',
                'ordering': ('creation_date',),
            },
        ),
        migrations.CreateModel(
            name='ContactMailingStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(-1, 'sent in test'), (0, 'sent'), (1, 'error'), (2, 'invalid email'), (4, 'opened'), (5, 'opened on site'), (6, 'link opened'), (7, 'unsubscription')], verbose_name='status')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='creation date')),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newsletter.Contact', verbose_name='contact')),
            ],
            options={
                'verbose_name': 'contact mailing status',
                'verbose_name_plural': 'contact mailing statuses',
                'ordering': ('creation_date',),
            },
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('url', models.CharField(max_length=255, verbose_name='url')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='creation date')),
            ],
            options={
                'verbose_name': 'link',
                'verbose_name_plural': 'links',
                'ordering': ('creation_date',),
            },
        ),
        migrations.CreateModel(
            name='MailingList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='creation date')),
                ('modification_date', models.DateTimeField(auto_now=True, verbose_name='modification date')),
                ('subscribers', models.ManyToManyField(related_name='mailinglist_subscriber', to='newsletter.Contact', verbose_name='subscribers')),
                ('unsubscribers', models.ManyToManyField(blank=True, related_name='mailinglist_unsubscriber', to='newsletter.Contact', verbose_name='unsubscribers')),
            ],
            options={
                'verbose_name': 'mailing list',
                'verbose_name_plural': 'mailing lists',
                'ordering': ('creation_date',),
            },
        ),
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('content', models.TextField(default='', help_text='Or paste an URL.', verbose_name='content')),
                ('header_sender', models.CharField(default='Emencia Newsletter<noreply@emencia.com>', max_length=255, verbose_name='sender')),
                ('header_reply', models.CharField(default='Emencia Newsletter<noreply@emencia.com>', max_length=255, verbose_name='reply to')),
                ('status', models.IntegerField(choices=[(0, 'draft'), (1, 'waiting sending'), (2, 'sending'), (4, 'sent'), (5, 'canceled')], default=0, verbose_name='status')),
                ('sending_date', models.DateTimeField(default=datetime.datetime.now, verbose_name='sending date')),
                ('slug', models.SlugField(help_text='Used for displaying the newsletter on the site.', unique=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='creation date')),
                ('modification_date', models.DateTimeField(auto_now=True, verbose_name='modification date')),
                ('mailing_lists', models.ManyToManyField(to='newsletter.MailingList', verbose_name='mailing lists')),
            ],
            options={
                'verbose_name': 'newsletter',
                'verbose_name_plural': 'newsletters',
                'ordering': ('creation_date',),
                'permissions': (('can_change_status', 'Kann Status ändern'),),
            },
        ),
        migrations.CreateModel(
            name='SMTPServer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('host', models.CharField(max_length=255, verbose_name='server host')),
                ('user', models.CharField(blank=True, help_text='Leave it empty if the host is public.', max_length=128, verbose_name='server user')),
                ('password', models.CharField(blank=True, help_text='Leave it empty if the host is public.', max_length=128, verbose_name='server password')),
                ('port', models.IntegerField(default=25, verbose_name='server port')),
                ('tls', models.BooleanField(verbose_name='server use TLS')),
                ('headers', models.TextField(blank=True, help_text='key1: value1 key2: value2, splitted by return line.', verbose_name='custom headers')),
                ('mails_hour', models.IntegerField(default=0, verbose_name='mails per hour')),
            ],
            options={
                'verbose_name': 'SMTP server',
                'verbose_name_plural': 'SMTP servers',
            },
        ),
        migrations.CreateModel(
            name='WorkGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('contacts', models.ManyToManyField(blank=True, to='newsletter.Contact', verbose_name='contacts')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.Group', verbose_name='permissions group')),
                ('mailinglists', models.ManyToManyField(blank=True, to='newsletter.MailingList', verbose_name='mailing lists')),
                ('newsletters', models.ManyToManyField(blank=True, to='newsletter.Newsletter', verbose_name='newsletters')),
            ],
            options={
                'verbose_name': 'workgroup',
                'verbose_name_plural': 'workgroups',
            },
        ),
        migrations.AddField(
            model_name='newsletter',
            name='server',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='newsletter.SMTPServer', verbose_name='smtp server'),
        ),
        migrations.AddField(
            model_name='newsletter',
            name='test_contacts',
            field=models.ManyToManyField(blank=True, to='newsletter.Contact', verbose_name='test contacts'),
        ),
        migrations.AddField(
            model_name='contactmailingstatus',
            name='link',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='newsletter.Link', verbose_name='link'),
        ),
        migrations.AddField(
            model_name='contactmailingstatus',
            name='newsletter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newsletter.Newsletter', verbose_name='newsletter'),
        ),
        migrations.AddField(
            model_name='attachment',
            name='newsletter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newsletter.Newsletter', verbose_name='newsletter'),
        ),
    ]