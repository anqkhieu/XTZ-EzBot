import discord
import os, sys, datetime

import json, requests

import matplotlib.pyplot as plt
import seaborn as sns

from discord.ext import commands
from pretty_help import PrettyHelp
from dotenv import load_dotenv

# Create Bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$', \
	description='<:xtz:896622154517446786>  **XTZ EzBot** is a Tezos blockchain bot. \
	Get quick and easy access to Tezos blockchain information, including price action graphs and account metadata queries. ', \
	help_command=PrettyHelp(no_category = 'Commands', show_index=False)
)

# Load Environment Variables
load_dotenv()
TOKEN = os.environ['TOKEN']
DEBUG = os.environ['DEBUG']

# Settings
sns.set_theme()

# Bot Commands
@bot.event
async def on_ready():
	print('TEZOS BOT - ONLINE')
	await bot.change_presence(activity=discord.Game(name='🍞 Baking Blocks'))

@bot.command(aliases=['price'], help="Get the prize of XTZ.")
async def ticker(ctx):
	price = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids=tezos&vs_currencies=usd").json()["tezos"]["usd"]
	chart = generate_price_chart(7)
	await ctx.send(embed=embed("Tezos Ticker", f"<:xtz:896622154517446786> = ${price} USD"))
	await ctx.send("------")
	await ctx.send("**TEZOS PRICE ACTION CHART**")
	await ctx.send(file=chart)
	await ctx.send("> Source: CoinGecko - <https://www.coingecko.com/en/coins/tezos>")

@bot.command(aliases=['ch'], help="Get the price action chart of XTZ, default 7 days (eg: !chart 240).")
async def chart(ctx, arg=7):
	chart = generate_price_chart(arg)
	await ctx.send("**TEZOS PRICE ACTION CHART**")
	await ctx.send(file=chart)
	await ctx.send("> Source: CoinGecko - <https://www.coingecko.com/en/coins/tezos>")

@bot.command(aliases=['versus'], help="Get the prize of XTZ versus another currency (eg: $vs ETH).")
async def vs(ctx, arg='usd'):
	price = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids=tezos&vs_currencies={arg.lower()}").json()["tezos"][arg]
	await ctx.send(embed=embed("Tezos Exchange Rate", f"1 XTZ is equivalent to {round(price, 6)} {arg.upper()}."))

@bot.command(aliases=['conv'], help="Convert an amount of currency to get the equivalent amount in XTZ (eg: !convert 4 ETH)")
async def convert(ctx, amount=1, curr='USD'):
	price = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids=tezos&vs_currencies={curr.lower()}").json()["tezos"][curr]
	await ctx.send(embed=embed("Approx. Tezos Conversion", f"{amount} {curr.upper()} would convert to approximately {round(amount/price, 6)} XTZ."))

@bot.command(aliases=['acc', 'accountInfo'], help="Get blockchain metadata associated with an address. (Eg: !account <address>)")
async def account(ctx, address='None'):
	if address == 'None': await ctx.send(embed=embed("Error", "You must specify an address to query.", discord.Colour.red()))
	try:
		metadata = requests.get(f"https://api.tzkt.io/v1/accounts/{address}/metadata").json()
		text = f"<:xtz:896622154517446786> **Wallet Address:** {address} \n\n"
		for key,value in metadata.items():
				text += f"{key.capitalize()} - {value} \n"
		await ctx.send(embed=embed("Tezos Account Info", text))
	except Exception as e:
		print(e)
		await ctx.send(embed=embed("Error", "That is not a valid address.", discord.Colour.red()))

@bot.command(aliases=['bal'], help="Get the XTZ balance of an address (eg: !balance <address>).")
async def balance(ctx, address='None'):
	if address == 'None': await ctx.send(embed=embed("Error", "You must specify an address to query.", discord.Colour.red()))
	try:
		# convert microtez to tez; format with commas
		bal = requests.get(f"https://api.tzkt.io/v1/accounts/{address}/balance").json() / 1000000
		bal = "{:,}".format(bal)
		text = f"**Wallet Address:** {address} \n**Balance:** {bal} XTZ"
		await ctx.send(embed=embed("<:xtz:896622154517446786> Tezos Account Balance", text))
	except Exception as e:
		print(e)
		await ctx.send(embed=embed("Error", "That is not a valid address.", discord.Colour.red()))

# Discord Embed Easy
def embed(title, description, color=discord.Colour.blue(), image = None):
	embed = discord.Embed(title=title, description=description, colour=color)
	return embed

# Generate Price Action Chart
def generate_price_chart(days=7):
	data = requests.get(f"https://api.coingecko.com/api/v3/coins/tezos/market_chart?vs_currency=usd&days={days}").json()["prices"]

	timestampData = []; priceData = []
	for value in data:
		timestampData.append(value[0])
		priceData.append(value[1])

	dateData = []
	today = datetime.date.today()
	for i in range(days): dateData.append(today - datetime.timedelta(days=i))

	plt.clf()
	plt.title(f"Tezos Price Action ({days} Days)")
	plt.plot(timestampData, priceData)
	plt.ylabel("Price (USD)", loc = 'center')
	plt.xlabel(str(today - datetime.timedelta(days=days))[5:10] + ' to ' + str(today)[5:10] + ' of ' + str(today)[:4], loc = 'center')
	plt.xticks([])
	plt.savefig('TezosPlot.png')
	return discord.File("TezosPlot.png", filename="TezosPlot.png")

bot.run(TOKEN)
