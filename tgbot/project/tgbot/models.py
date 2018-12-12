import re

import requests
from django.db import models
from django.db.models.functions import Length
from mptt.models import MPTTModel, TreeForeignKey
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
CANCEL_NAME = "Назад"


class BotCommand(MPTTModel):
    GET = 1
    POST = 2
    PATCH = 3
    DELETE = 4
    METHOD_CHOICES = (
        (GET, "GET"),
        (POST, "POST"),
        (PATCH, "PATCH"),
        (DELETE, "DELETE")
    )

    url = models.CharField(max_length=256, blank=True, null=True)
    method = models.PositiveSmallIntegerField(choices=METHOD_CHOICES, default=GET)
    name = models.CharField(max_length=255)
    parent = TreeForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)

    def process(self, tg_update):
        if BotCommand.objects.filter(parent=self).exists():  # have submenu
            button_list = [[x.name for x in BotCommand.objects.filter(parent=self)], [CANCEL_NAME]]
            reply_markup = ReplyKeyboardMarkup(button_list)
            tg_update.message.reply_text(self.message, reply_markup=reply_markup)
        else:  # need text answer
            # у которых нет saved_params и нет заполненных значений
            try:
                saved_post_parameters = SavedPostParameter.objects.filter(tg_user_id=tg_update.message.from_user.id,
                                                                          post_parameter__bot_command=self)
                saved_get_parameters = SavedUrlParameter.objects.filter(tg_user_id=tg_update.message.from_user.id,
                                                                        url_parameter__bot_command=self)
                prepared_to_fill_post_parameter = (
                        saved_post_parameters.filter(value="") | saved_post_parameters.filter(
                    value__isnull=True)).first()
                prepared_to_fill_get_parameter = (saved_get_parameters.filter(value="") | saved_get_parameters.filter(
                    value__isnull=True)).first()
                if not prepared_to_fill_get_parameter and not prepared_to_fill_post_parameter:
                    param_to_fill = list(self.get_unfilled_parameters(uid=tg_update.message.from_user.id))[0]
                    tg_update.message.reply_text("Введите {}".format(param_to_fill.name),
                                                 reply_markup=ReplyKeyboardRemove())

                    if isinstance(param_to_fill, QueryParameter):
                        SavedUrlParameter.objects.create(url_parameter=param_to_fill,
                                                         tg_user_id=tg_update.message.from_user.id)
                    else:
                        SavedPostParameter.objects.create(post_parameter=param_to_fill,
                                                          tg_user_id=tg_update.message.from_user.id)
                else:
                    if prepared_to_fill_get_parameter:
                        prepared_to_fill_get_parameter.value = tg_update.message.text
                        prepared_to_fill_get_parameter.save()
                    else:
                        if re.match(prepared_to_fill_post_parameter.post_parameter.regex, tg_update.message.text):
                            prepared_to_fill_post_parameter.value = tg_update.message.text
                            prepared_to_fill_post_parameter.save()
                        else:
                            tg_update.message.reply_text(
                                "Неверный формат ввода. Значение должно соответствовать регулярному выражению '{}'".format(
                                    prepared_to_fill_post_parameter.post_parameter.regex),
                                reply_markup=ReplyKeyboardRemove())
                            return
                    param_to_fill = list(self.get_unfilled_parameters(uid=tg_update.message.from_user.id))[0]
                    if isinstance(param_to_fill, QueryParameter):
                        SavedUrlParameter.objects.create(url_parameter=param_to_fill,
                                                         tg_user_id=tg_update.message.from_user.id)
                    else:
                        SavedPostParameter.objects.create(post_parameter=param_to_fill,
                                                          tg_user_id=tg_update.message.from_user.id)
                    tg_update.message.reply_text("Введите {}".format(param_to_fill.name),
                                                 reply_markup=ReplyKeyboardRemove())
            except IndexError as e:  # no more params to fill

                if self.url:
                    url_params_string = '&'.join('='.join((x.key, x.value)) for x in (
                            self.url_params.annotate(text_len=Length('value')).filter(text_len__gt=0,
                                                                                      is_header=False) | self.url_params.filter(
                        value__isnull=False, is_header=False)))
                    saved_url_parameters = SavedUrlParameter.objects.filter(url_parameter__bot_command=self,
                                                                            tg_user_id=tg_update.message.from_user.id,
                                                                            url_parameter__is_header=False)
                    if saved_url_parameters:
                        url_params_string += '&' + '&'.join(
                            ['='.join((x.url_parameter.key, x.value)) for x in saved_url_parameters])

                    post_params_dict = {x.key: x.value for x in (
                            self.post_params.annotate(text_len=Length('value')).filter(
                                text_len__gt=0) | self.post_params.filter(value__isnull=False))}
                    for f in SavedPostParameter.objects.filter(tg_user_id=tg_update.message.from_user.id,
                                                               post_parameter__bot_command=self):
                        post_params_dict[f.post_parameter.key] = f.value
                    for k, v in post_params_dict.items():
                        if v.lower() == 'false':
                            post_params_dict[k] = False
                        elif v.lower() == 'true':
                            post_params_dict[k] = True
                        elif re.match('^\d+$', v):
                            post_params_dict[k] = int(v)
                        elif re.match('^\d+.\d+$', v):
                            post_params_dict[k] = float(v)
                    headers_dict = {x.key: x.value for x in (
                            self.url_params.annotate(text_len=Length('value')).filter(text_len__gt=0,
                                                                                      is_header=True) | self.url_params.filter(
                        value__isnull=False, is_header=True))}
                    for f in SavedUrlParameter.objects.filter(tg_user_id=tg_update.message.from_user.id,
                                                              url_parameter__bot_command=self,
                                                              url_parameter__is_header=True):
                        headers_dict[f.url_parameter.key] = f.value
                    try:
                        if self.method == self.GET:
                            answer = requests.get(self.url + '?' + url_params_string, headers=headers_dict,
                                                  verify=False).text
                        else:
                            answer = requests.post(self.url + '?' + url_params_string, headers=headers_dict,
                                                   verify=False,
                                                   data=post_params_dict).text
                        tg_update.message.reply_text(answer[:4096])
                    except Exception as e:
                        tg_update.message.reply_text(f"Something went wrong: {e}")
                else:
                    tg_update.message.reply_text("URL required")

                SavedPostParameter.objects.filter(tg_user_id=tg_update.message.from_user.id).delete()
                SavedUrlParameter.objects.filter(tg_user_id=tg_update.message.from_user.id).delete()
                LastCommand.objects.filter(tg_user_id=tg_update.message.from_user.id).delete()
            except Exception as e1:
                tg_update.message.reply_text(f"Fatal error. {e1}")

    def get_unfilled_parameters(self, uid):
        unprefilled_post_parameters = PostParam.objects.filter(value="", bot_command=self) | PostParam.objects.filter(
            value__isnull=True, bot_command=self)
        unprefilled_url_parameters = QueryParameter.objects.filter(value="",
                                                                   bot_command=self) | QueryParameter.objects.filter(
            value__isnull=True, bot_command=self)
        for pp in unprefilled_post_parameters:
            if not SavedPostParameter.objects.filter(post_parameter=pp, tg_user_id=uid).first():
                yield pp

        for up in unprefilled_url_parameters:
            if not SavedUrlParameter.objects.filter(url_parameter=up, tg_user_id=uid).first():
                yield up

    def __str__(self):
        return self.name


class QueryParameter(models.Model):
    key = models.CharField(max_length=20)
    value = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=20)
    bot_command = models.ForeignKey(BotCommand, related_name='url_params', on_delete=models.CASCADE)
    is_header = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class PostParam(models.Model):
    name = models.CharField(max_length=20)
    key = models.CharField(max_length=20)
    value = models.CharField(max_length=255, blank=True, null=True)
    bot_command = models.ForeignKey(BotCommand, related_name='post_params', on_delete=models.CASCADE)
    regex = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class LastCommand(models.Model):
    tg_user_id = models.BigIntegerField(unique=True)
    command = models.ForeignKey(BotCommand, on_delete=models.CASCADE)

    def __str__(self):
        return self.command.name


class SavedPostParameter(models.Model):
    post_parameter = models.ForeignKey(PostParam, on_delete=models.CASCADE)
    value = models.TextField(blank=True, null=True)
    tg_user_id = models.BigIntegerField()

    def __str__(self):
        return self.post_parameter.name


class SavedUrlParameter(models.Model):
    url_parameter = models.ForeignKey(QueryParameter, on_delete=models.CASCADE)
    value = models.TextField(blank=True, null=True)
    tg_user_id = models.BigIntegerField()

    def __str__(self):
        return self.url_parameter.name
