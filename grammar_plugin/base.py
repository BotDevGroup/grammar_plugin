# -*- coding: utf-8 -*-
from marvinbot.plugins import Plugin
from marvinbot.handlers import CommandHandler
import logging
import requests
import json

log = logging.getLogger(__name__)


class GrammarPlugin(Plugin):
    def __init__(self):
        super(GrammarPlugin, self).__init__('grammar_plugin')
        self.config = None

    def get_default_config(self):
        return {
            'short_name': self.name,
            'enabled': True,
            'base_url': 'https://languagetool.org/api/v2/check',
            'language': 'en-US'
        }

    def configure(self, config):
        self.config = config

    def setup_handlers(self, adapter):
        log.info("Setting up handlers for Grammar plugin")
        self.add_handler(CommandHandler('grammar', self.on_grammar_command,
                                        command_description='Checks the grammar on the text being replied to.'))

    def setup_schedules(self, adapter):
        pass

    def on_grammar_command(self, update):
        message = update.effective_message

        if message.reply_to_message is None:
            message.reply_text(text='❌ When checking grammar, use this command while replying.')

        text = message.reply_to_message.text
        try:
          data = self.fetch_corrections(text)
        except:
            message.reply_text(text='❌ An error occurred while checking the grammar')
            return

        log.info(json.dumps(data))

        responses = []
        for match in data.get('matches'):
            context = match.get('context', {}).get('text', '')
            offset = match.get('context', {}).get('offset', 0)
            length = match.get('context', {}).get('length', 0)
            decorated = '{}<b>{}</b>{}'.format(
                context[:offset],
                context[offset:offset + length],
                context[offset + length:]
            )
            suggestions = ', '.join([kvp.get('value', '') for kvp in match.get('replacements', [])[:5]])
            response = '✏️ <b>{}</b>\n{}'.format(match.get('message'), decorated)
            if len(suggestions) > 0:
                response += '\n<b>Suggestions:</b> {}'.format(suggestions)

            responses.append(response)

        message.reply_text(text='\n\n'.join(responses)[:4096], parse_mode='HTML')

    def fetch_corrections(self, text):
        payload = {
            'text': text,
            'language': self.config.get('language')
        }
        url = self.config.get('base_url')
        response = requests.post(url, data=payload)
        return response.json()
