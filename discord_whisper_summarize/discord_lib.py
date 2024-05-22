import io
import os

import pydub  # pip install pydub==0.25.1

import discord
from discord.sinks import MP3Sink
from discord.ext import commands
from . import open_ai_lib


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


async def finished_callback(sink: MP3Sink, channel: discord.TextChannel):
    mention_strs = []
    audio_segs: list[pydub.AudioSegment] = []
    files: list[discord.File] = []

    longest = pydub.AudioSegment.empty()

    for user_id, audio in sink.audio_data.items():
        mention_strs.append(f"<@{user_id}>")

        seg = pydub.AudioSegment.from_file(audio.file, format="mp3")

        # Determine the longest audio segment
        if len(seg) > len(longest):
            audio_segs.append(longest)
            longest = seg
        else:
            audio_segs.append(seg)

        audio.file.seek(0)
        files.append(discord.File(audio.file, filename=f"{user_id}.mp3"))

    for seg in audio_segs:
        longest = longest.overlay(seg)

    with io.BytesIO() as f:
        longest.export(f, format="mp3")
        summarizer = open_ai_lib.OpenAILib()
        with open(f"{'_'.join(mention_strs)}.mp3", "wb") as file:
            file.write(f.getbuffer())
            file.close()

        with open(f"{'_'.join(mention_strs)}.mp3", "rb") as file:
            transcription = summarizer.transcribe_audio(file)
            message = await channel.send("文字起こし中")
            meeting_minutes = summarizer.meeting_minutes(transcription)
            await message.edit(content="文字起こし完了。議事録作成中")
            await channel.send(
                content=f"""
議事録 参加者: {', '.join(mention_strs)}
------
全体の概要
{meeting_minutes["abstract_summary"]}
------
{meeting_minutes["action_items"]}
------
{meeting_minutes["key_points"]}
------
感情分析
{meeting_minutes["sentiment"]}
------
                """
            )


@bot.command()
async def join(ctx: discord.ApplicationContext):
    """Join the voice channel!"""
    voice = ctx.author.voice

    if not voice:
        return await ctx.send("You're not in a vc right now")

    await voice.channel.connect()

    await ctx.send("Joined!")


@bot.command()
async def start(ctx: discord.ApplicationContext):
    """Record the voice channel!"""
    voice = ctx.author.voice

    if not voice:
        return await ctx.send("You're not in a vc right now")

    vc: discord.VoiceClient = ctx.voice_client

    if not vc:
        return await ctx.send("I'm not in a vc right now. Use `/join` to make me join!")

    vc.start_recording(
        MP3Sink(),
        finished_callback,
        ctx.channel,
    )

    await ctx.send("The recording has started!")


@bot.command()
async def stop(ctx: discord.ApplicationContext):
    """Stop the recording"""
    vc: discord.VoiceClient = ctx.voice_client

    if not vc:
        return await ctx.send("There's no recording going on right now")

    vc.stop_recording()
    vc.disconnect()

    await ctx.send("The recording has stopped!")


@bot.command()
async def leave(ctx: discord.ApplicationContext):
    """Leave the voice channel!"""
    vc: discord.VoiceClient = ctx.voice_client

    if not vc:
        return await ctx.send("I'm not in a vc right now")

    await vc.disconnect()

    await ctx.send("Left!")


def run_bot():
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))
