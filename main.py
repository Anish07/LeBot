from typing import Final
import os

import discord
import requests
from dotenv import load_dotenv
from discord import Intents, Client, Message, Embed
import random
import webserver
from datetime import datetime

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
API_SPORTS_KEY = os.getenv('API_SPORTS_KEY')

# STEP 1: BOT SETUP
intents: Intents = Intents.default()
intents.message_content = True  # NOQA
client: Client = Client(intents=intents)


# Function to fetch schedules from The Sports DB
def get_nflschedule(league, season):
    url = f"https://v1.american-football.api-sports.io/games?league={league}&season={season}&date={datetime.today().strftime('%Y-%m-%d')}&timezone=America/Toronto"
    headers = {
        'x-apisports-key': API_SPORTS_KEY
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    image_url = "https://seeklogo.com/images/N/nfl-logo-71004E6076-seeklogo.com.png"

    if "response" in data:
        events = data["response"]
        schedule = []
        for event in events[:10]:  # Get only the first 5 events
            match = f"{event['game']['stage']} - {event['game']['week']}: {event['teams']['home']['name']} vs {event['teams']['away']['name']} at {event['game']['date']['time']}"
            schedule.append(match)
        schedule.append(image_url)
        return schedule
    else:
        print("No events found or invalid response from API.")
        return None


def get_plschedule(league, season, matchday):
    url = f"https://v3.football.api-sports.io/fixtures?league={league}&season={season}&round=Regular%20Season%20-%20{matchday}&timezone=America/Toronto"
    headers = {
        'x-apisports-key': API_SPORTS_KEY
    }
    response = requests.get(url, headers=headers)
    data = response.json()

    if "response" in data:
        events = data["response"]
        schedule = []
        image_url = ""

        for event in events[:10]:  # Get only the first 5 events
            datetime_string = f"{event['fixture']['date']}"

            # Parse the string into a datetime object
            dt = datetime.fromisoformat(datetime_string)

            # Extract the date and time
            date_part = dt.date()  # Outputs: 2024-08-16
            time_part = dt.strftime('%H:%M')  # Outputs: 15:00

            match = f"{event['teams']['home']['name']} vs {event['teams']['away']['name']} on {date_part} at {time_part}"
            schedule.append(match)
            image_url = event['league']['logo']

        schedule.append(image_url)

        return schedule
    else:
        print("No events found or invalid response from API.")
        return None


# List of LeBron James quotes
lebron_quotes = [
    "I like criticism. It makes you strong.",
    "You can't be afraid to fail. It's the only way you succeed - you're not gonna succeed all the time, and I know that.",
    "I think the reason why I am who I am today is because I went through those tough times when I was younger.",
    "Dream as if you’ll live forever. Live as if you’ll die today.",
    "I treated it like every day was my last day with a basketball.",
    "I have short goals – to get better every day, to help my teammates every day – but my only ultimate goal is to win an NBA championship.",
    "Warren Buffett told me that he always preferred buying company’s stocks at a time when he felt that they were undervalued. That was the exact situation when I bought the pizza joint.",
    "You have to be able to accept failure to get better.",
    "I always say, decisions I make, I live with them. There’s always ways you can correct them or ways you can do them better. At the end of the day, I live with them.",
    "I'm going to use all my tools, my God-given ability, and make the best life I can with it.",
    "Yea that’s my favourite saying",
]
# List of LeBron James images
lebron_images = [
    "https://i.imgur.com/7OjKM2j.jpeg"
    "https://i.imgur.com/FPRu7sw.mp4"
]


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower() == "!lequote":
        print("Received !lequote command")  # Debugging statement
        quote = random.choice(lebron_quotes)
        image_url = random.choice(lebron_images)
        embed = Embed(description=f"\"{quote}\"", color=0x00ff00)
        embed.set_author(name="LeBron James")
        embed.set_image(url=image_url)
        await message.channel.send(embed=embed)
        print("Sent the quote and image")  # Debugging statement

    lecrymeme = "../lecrymeme.mp4"

    if message.content.lower() == "!leman":
        print("Received !LeMan command")  # Debugging statement
        if os.path.exists(lecrymeme):
            with open(lecrymeme, 'rb') as video_file:
                await message.channel.send(file=discord.File(lecrymeme, "lecrymeme.mp4"))
            print("Sent the video")  # Debugging statement
        else:
            await message.channel.send("Sorry, I couldn't find the video file.")
            print("Video file not found")  # Debugging statement

    if message.content.lower() == "!nflschedule":
        print("Received !nflschedule command")
        nfl_league_id = "1"  # Replace with the actual NFL league ID in API-Sports
        schedule = get_nflschedule(nfl_league_id, "2024")
        if schedule:
            response = "\n".join(schedule)
            await message.channel.send(f"**Today's NFL Games**\n{response}")
        else:
            await message.channel.send("Sorry, I couldn't retrieve the NFL schedule.")

    if message.content.startswith("!plschedule"):
        print("Received !plschedule command")
        pl_league_id = "39"  # Replace with the actual NFL league ID in API-Sports

        try:
            # Split the message to get the command and possibly the argument
            command_parts = message.content.split()

            if len(command_parts) > 1:
                # If a number is provided, parse it as an integer
                match_day = int(command_parts[1])
            else:
                # If no number is provided, use the default value, such as the next match day
                match_day = 1

            # Fetch the schedule for the specified match day
            schedule = get_plschedule(pl_league_id, "2024", match_day)
            if schedule:
                response = f"**Premier League - Match Day {match_day}**\n" + "\n".join(schedule)
                await message.channel.send(response)
            else:
                await message.channel.send(f"Sorry, I couldn't retrieve the schedule for match day {match_day}.")

        except ValueError:
            # Handle cases where the provided argument isn't a valid integer
            await message.channel.send("Please provide a valid match day number. Example: `!plschedule 3`")

webserver.keep_alive()
client.run(TOKEN)


# STEP 5: MAIN ENTRY POINT
def main() -> None:
    client.run(token=TOKEN)


if __name__ == '__main__':
    main()
