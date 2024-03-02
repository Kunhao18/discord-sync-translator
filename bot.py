import discord

from utils import client, tree
from utils import bot_token, guild_id, webhook_name
from utils import ch_manager, translator_backend, detector_backend
from translator import TranslationParser
from commands import ChannelOpGroup, GroupOpGroup


@client.event
async def on_ready():
    for channel_id in ch_manager.channel_dict.keys():
        if client.get_channel(int(channel_id)) is None:
            print(f'Unbound invalid channel: {channel_id}')
            ch_manager.unbind_channel(channel_id)
    channel_op_group = ChannelOpGroup(name="channel", description="channel operations.")
    group_op_group = GroupOpGroup(name="group", description="group operations.")
    tree.add_command(channel_op_group)
    tree.add_command(group_op_group)
    tree.copy_global_to(guild=discord.Object(id=guild_id))
    await tree.sync(guild=discord.Object(id=guild_id))
    print('Bot started...')


@client.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content.strip() == "" and \
       message.attachments == [] and \
       message.embeds == []:
        return
    channel_id = str(message.channel.id)
    if channel_id in ch_manager.channel_dict:
        group_name = ch_manager.channel_dict[channel_id]
        trans_targets = {k: v for k, v in ch_manager.group_dict[group_name].items() if v != channel_id}

        trans_parser = TranslationParser(detector_backend, translator_backend)
        trans_parser.load_input(message)

        for lang, cur_id in trans_targets.items():
            send_content, send_embeds, send_attachment_urls = \
                trans_parser.translate_message(lang)
            send_urls = "\n".join(send_attachment_urls)
            send_content = "\n".join([send_content, send_urls]) if send_content else send_urls
            cur_channrl = client.get_channel(int(cur_id))
            
            if cur_channrl:
                webhooks = await cur_channrl.webhooks()
                cur_webhook = None
                for webhook in webhooks:
                    if webhook.name == webhook_name:
                        cur_webhook = webhook
                        break
                if cur_webhook is None:
                    cur_webhook = await cur_channrl.create_webhook(name=webhook_name)
                user_name = message.author.display_name if message.author.display_name is not None else message.author.name
                avatar_url = message.author.avatar.url if message.author.avatar else None
                await cur_webhook.send(content=str(send_content),
                                       embeds=send_embeds,
                                       username=user_name, 
                                       avatar_url=avatar_url)
            else:
                ch_manager.unbind_channel(int(cur_id))


if __name__ == '__main__':
    client.run(bot_token)
