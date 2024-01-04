import discord
from discord import app_commands

from utils import admin_check
from utils import client
from utils import ch_manager
from utils import webhook_name
from utils import lang_dict_emoji
from view import ChannelBindView, ChannelChangeView


class ChannelOpGroup(app_commands.Group):
    @app_commands.command(name="bind",
                          description="Bind new channel.")
    @admin_check()
    async def bind(self, interaction, channel: discord.TextChannel, group_name: str):
        channel_id = str(channel.id)
        if channel_id in ch_manager.channel_dict.keys():
            await interaction.response.send_message(content="**[FAIL]** Channel already bound.", ephemeral=True)
        elif group_name not in ch_manager.group_dict.keys():
            await interaction.response.send_message(content="**[FAIL]** Group doesn't exist.", ephemeral=True)
        else:
            bind_view = ChannelBindView(channel, channel_id, group_name, ch_manager, webhook_name=webhook_name)
            await interaction.response.send_message(content="Please select the langauge...", 
                                                    view=bind_view, ephemeral=True)

    @app_commands.command(name="unbind",
                          description="Unbind channel.")
    @admin_check()
    async def unbind(self, interaction, channel: discord.TextChannel):
        channel_id = str(channel.id)
        if channel_id not in ch_manager.channel_dict.keys():
            await interaction.response.send_message(content="**[FAIL]** Channel isn't bound.", ephemeral=True)
        else:
            unbind_result = ch_manager.unbind_channel(channel_id)
            await interaction.response.send_message(content=unbind_result, ephemeral=True)

    @app_commands.command(name="change",
                          description="Change channel group and language.")
    @admin_check()
    async def change(self, interaction, channel: discord.TextChannel, new_group: str):
        channel_id = str(channel.id)
        if channel_id not in ch_manager.channel_dict.keys():
            await interaction.response.send_message(content="**[FAIL]** Channel isn't bound.", ephemeral=True)
        elif new_group not in ch_manager.group_dict.keys():
            await interaction.response.send_message(content="**[FAIL]** Group doesn't exist.", ephemeral=True)
        else:
            bind_view = ChannelChangeView(channel_id, new_group, ch_manager)
            await interaction.response.send_message(content="Please select the langauge...", 
                                                    view=bind_view, ephemeral=True)


class GroupOpGroup(app_commands.Group):
    @app_commands.command(name="check",
                          description="Check group infos.")
    @admin_check()
    async def check(self, interaction):
        check_result, group_dict = ch_manager.check_group()
        if check_result.startswith("**[FAIL]**"):
            await interaction.response.send_message(content=check_result, ephemeral=True)
            return
        full_info = [check_result]
        for k, v in group_dict.items():
            full_info.append(f"- {k}")
            for k_i, v_i in v.items():
                if client.get_channel(int(v_i)):
                    full_info.append(f" - {lang_dict_emoji[k_i]}: <#{v_i}>")
                else:
                    ch_manager.unbind_channel(int(v_i))
        full_msg = "\n".join(full_info)
        await interaction.response.send_message(content=full_msg, ephemeral=True)

    @app_commands.command(name="create",
                          description="Create new group.")
    @admin_check()
    async def create(self, interaction, group_name: str):
        create_result = ch_manager.create_group(group_name)
        await interaction.response.send_message(content=create_result, ephemeral=True)

    @app_commands.command(name="delete",
                          description="Delete group.")
    @admin_check()
    async def delete(self, interaction, group_name: str):
        delete_result = ch_manager.delete_group(group_name)
        await interaction.response.send_message(content=delete_result, ephemeral=True)

    @app_commands.command(name="rename",
                          description="Change group ID.")
    @admin_check()
    async def rename(self, interaction, group_name: str, new_name: str):
        if group_name == new_name:
            await interaction.response.send_message(content="**[FAIL]** Same names.", ephemeral=True)
        else:
            rename_result = ch_manager.rename_group(group_name, new_name)
            await interaction.response.send_message(content=rename_result, ephemeral=True)
            