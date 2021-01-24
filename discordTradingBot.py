
import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup


import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("INSERT FIREBASE JSON FILE PATH")
default_app = firebase_admin.initialize_app(cred)

db = firestore.client()

client  = commands.Bot(command_prefix = '!')

@client.event
async def on_ready():
  print('Bot is ready.')

@client.command()
async def check(ctx, *, phraseC):
    priceC = ("$"+(BeautifulSoup((requests.get("https://finance.yahoo.com/quote/"+phraseC+"?p="+phraseC)).content, "html.parser").find_all("div", {"class":"My(6px) Pos(r) smartphone_Mt(6px)"})[0].find("span").text))
    await ctx.send(f'The price of {phraseC} is: {priceC}')

@client.command()
async def leaderboard(ctx):
  await ctx.send(f'1st Place: \n2nd Place: \n3rd Place: \n4th Place: \n5th place: ')

@client.command()
async def sell(ctx, *, phrase):
  location = phrase.find(' ')
  phraseTicker=phrase[0:location]
  phraseQuantity=phrase[location+1:len(phrase)]
  code=phraseTicker

  userTotal=ctx.message.author.name
  price = ("$"+(BeautifulSoup((requests.get("https://finance.yahoo.com/quote/"+code+"?p="+code)).content, "html.parser").find_all("div", {"class":"My(6px) Pos(r) smartphone_Mt(6px)"})[0].find("span").text))
  price2 = ((BeautifulSoup((requests.get("https://finance.yahoo.com/quote/"+code+"?p="+code)).content, "html.parser").find_all("div", {"class":"My(6px) Pos(r) smartphone_Mt(6px)"})[0].find("span").text))
  price2 = price2.replace(',', '')
  total=float(price2)
  total = total*int(phraseQuantity)
  ftotal=round(total, 2)



  await ctx.send(f'{userTotal} sold {phraseQuantity} {phraseTicker} shares at ${price2} at a total of ${ftotal}')

@client.command()
async def buy(ctxB, *, phraseB):

  userAcc=ctxB.message.author.name

  doc_ref = db.collection(u'users').document((u'{}').format(userAcc))

  locationB = phraseB.find(' ')
  phraseTickerB=phraseB[0:locationB]
  phraseQuantityB=phraseB[locationB+1:len(phraseB)]
  codeB=phraseTickerB
  priceB = ("$"+(BeautifulSoup((requests.get("https://finance.yahoo.com/quote/"+codeB+"?p="+codeB)).content, "html.parser").find_all("div", {"class":"My(6px) Pos(r) smartphone_Mt(6px)"})[0].find("span").text))
  price2B = ((BeautifulSoup((requests.get("https://finance.yahoo.com/quote/"+codeB+"?p="+codeB)).content, "html.parser").find_all("div", {"class":"My(6px) Pos(r) smartphone_Mt(6px)"})[0].find("span").text))
  price2B = price2B.replace(',', '')
  totalB=float(price2B)*int(phraseQuantityB)
  ftotalB=round(totalB, 2)

  doc = doc_ref.get()
  cashV=doc.get('cashValue')
  if doc.exists:
    if doc.get('cashValue') > ftotalB:
      doc_ref.set({
      u'stocks': doc.get('stocks') + u'{}{}'.format(phraseQuantityB, phraseTickerB),
      u'portfolio': doc.get('portfolio') + ftotalB,
      u'cashValue': doc.get('cashValue')-ftotalB
      })
      await ctxB.send(f'You bought {phraseQuantityB} {phraseTickerB} shares at ${price2B} at a total of ${ftotalB}')
    
    else:
      await ctxB.send(f'You do not have enough money. Current cash balance: ${cashV}')

  

@client.command()
async def commands(ctx):
  allcommands = "!commands is to view all commands\n!buy (enter ticker symbol) (enter quantity)\n!check (enter ticker symbol)\n!sell (enter ticker symbol) (enter quantity)\n!createAccount to create an account\n!account to check balance and portfolio of your account"
  await ctx.send(f'These are all the commands:\n\n{allcommands}')

@client.command()
async def account(ctx):
  userAcc=ctx.message.author.name
  doc_ref = db.collection(u'users').document((u'{}').format(userAcc))
  doc = doc_ref.get()
  if doc.exists:
    doc = doc_ref.get()
    pVal = doc.get('portfolio')
    ownedStocks =  doc.get('stocks')
    CashAcc = doc.get('cashValue')
    
    CashAcc=round(CashAcc, 2)
    pVal=round(pVal, 2)

    await ctx.send(f'Your portfolio value is: ${pVal}\nYou currently own: {ownedStocks}\nCash in account: ${CashAcc}')
  else:
    await ctx.send(f'Create an account with the command !createAccount')
  

@client.command()
async def createAccount(ctxC):
  userAcc=ctxC.message.author.name
  doc_ref = db.collection(u'users').document((u'{}').format(userAcc))
  doc = doc_ref.get()
  if doc.exists:
    await ctxC.send(f'You already made an account! Enter !commands to see what you can do')
  else:
    doc_ref = db.collection(u'users').document((u'{}').format(userAcc))
    doc_ref.set({
    u'stocks': u' ',
    u'portfolio': 0,
    u'cashValue': 10000
    })   
    await ctxC.send(f'You now have an account!')

  

client.run('DISCORD SERVER PATH')

