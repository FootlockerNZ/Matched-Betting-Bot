import requests
import ctypes
import sys
import traceback
import threading
import discord
import json
from datetime import datetime, timedelta
from colorama import init
from time import sleep
from discord import app_commands
from discord.ext import commands
from classes.logger import logger
log = logger().log
init()


ctypes.windll.kernel32.SetConsoleTitleW("Unity Utility Bot")

bookmakers = ['sportsbet', 'tab', 'tabnz', 'bet365', 'betdeluxe', 'betright', 'betr', 'bluebet', 'crossbet', 'elitebet', 'palmerbet', 'picklebet', 'ladbrokes', 'neds', 'pointsbet', 'realbookie', 'tab touch', 'topsport', 'unibet']

currencies = ['NZD']

bookmaker_choices = [app_commands.Choice(name=bookie, value=bookie) for bookie in bookmakers]

currency_choices = [app_commands.Choice(name=currency, value=currency) for currency in currencies]


bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())


def formatDate(date):
    input_datetime = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    new_datetime = input_datetime + timedelta(hours=12)
    hour = new_datetime.hour

    if hour == 0:
        formatted_hour = 12
        am_pm = 'AM'
    elif hour < 12:
        formatted_hour = hour
        am_pm = 'AM'
    elif hour == 12:
        formatted_hour = 12
        am_pm = 'PM'
    else:
        formatted_hour = hour - 12
        am_pm = 'PM'

    formatted_datetime_str = new_datetime.strftime(f"{formatted_hour}:{new_datetime.strftime('%M')}{am_pm} on %d/%m")

    return formatted_datetime_str



def reformatDate(date):
    try:
        sp = date.split('-')
        month = sp[1]
        date = sp[2].split(' ')[0] 
        return date+'/'+month
    except:
        return ''



def checkDate(date, beforeDate):
    bdS = beforeDate.split('/')
    dS = date.split('/')

    if int(bdS[1]) > int(dS[1]):
        return True
    else:
        if int(bdS[1]) == int(dS[1]) and int(bdS[0] > dS[0]):
            return True
        
    return False



def formatDate1(beforeDate):
    try:
        sp = beforeDate.split('/')
        if len(sp[0]) == 1:
            sp[0] = '0' + sp[0]
        if len(sp[1]) == 1:
            sp[1] = '0' + sp[1]
        formattedDate = '/'.join(sp)
    except:
        formattedDate = ''
    return formattedDate



def getConversions(bookmaker, session, liquidity, maxLay, beforeDate):
    try:
        slug = '[SNR CONVERSIONS] : '
        l = login(session)
        if l[0]:
            pass
        else:
            return l[1]
        nonce = getNonce(session)
        if 'Error' in nonce:
            return nonce
        
        log(slug+'Getting conversions...')
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'priority': 'u=1, i',
            'referer': 'https://bonusbank.com.au/matched-betting-software/',
            'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'x-wp-nonce': nonce,
        }

        params = {
            'type': 'premium',
        }

        try:
            r = session.get(
                'https://bonusbank.com.au/wp-json/bonusbank/v1/all-mongo/',
                params=params,
                headers=headers,
            )
        except:
            log(slug+'Failed to connect to bonus bank')
            return 'Error connecting to site.'

        conversions = []

        if r.status_code == 200:
            for i in r.json():
                if beforeDate != '':
                    date = reformatDate(i['date'])
                    if i['bookmaker'].lower() == bookmaker.lower() and i['liquidity'] > liquidity and i['lay'] < maxLay and checkDate(date, beforeDate) == True:
                        if i not in conversions:
                            conversions.append(i)
                else:
                    if i['bookmaker'].lower() == bookmaker.lower() and i['liquidity'] > liquidity and i['lay'] < maxLay:
                        if i not in conversions:
                            conversions.append(i)

            sorted_conversions = sorted(conversions, key=lambda x: x['snr_rating'], reverse=True)

            value = ''
            for i in sorted_conversions[0:6]:
                snr = f"{i['snr_rating']:.2f}"
                
                if i['source'] is None:
                    value += f"{i['event_name']}**,** {i['bet']}**,** {str(snr)}%**,** ${str(i['liquidity'])}**,** {str(i['back'])}/{str(i['lay'])}**,** {formatDate(i['date'])}**,** [Betfair]({i['betfair_source']})\n"
                else:
                    if bookmaker.lower() == 'bet365':
                        i['source'] = i['source'].replace('<STATE>', 'z1')
                    value += f"[{i['event_name']}]({i['source'].replace('au//', 'au/')})**,** {i['bet']}**,** {str(snr)}%**,** ${str(i['liquidity'])}**,** {str(i['back'])}/{str(i['lay'])}**,** {formatDate(i['date'])}**,** [Betfair]({i['betfair_source']})\n"

                value.replace('http://', 'https://\u200B').replace('<STATE>', 'z1')
                
            log(slug+'Successfully got SNR conversions')    
            return value
        else:
            log(slug+'Error requesting conversions. Code: '+str(r.status_code))
            return 'Error requesting conversions. Code: '+str(r.status_code)
        
    except Exception as e:
        log(slug+'Error getting conversions. Error: '+str(e))
        log(slug+' Traceback: {}'.format(traceback.format_exc())) 
        return 'Error getting conversions. Error: '+str(e)
    


def getSR(bookmaker, session, liquidity, maxLay, beforeDate):
    try:
        slug = '[SR CONVERSIONS] : '
        l = login(session)
        if l[0]:
            pass
        else:
            return l[1]
        nonce = getNonce(session)
        if 'Error' in nonce:
            return nonce
        
        log(slug+'Getting conversions...')
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'priority': 'u=1, i',
            'referer': 'https://bonusbank.com.au/matched-betting-software/',
            'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'x-wp-nonce': nonce,
        }

        params = {
            'type': 'premium',
        }

        try:
            r = session.get(
                'https://bonusbank.com.au/wp-json/bonusbank/v1/all-mongo/',
                params=params,
                headers=headers,
            )
        except:
            log(slug+'Failed to connect to bonus bank')
            return 'Error connecting to site.'

        conversions = []

        if r.status_code == 200:
            for i in r.json():
                
                if beforeDate != '':
                    date = reformatDate(i['date'])
                    if i['bookmaker'].lower() == bookmaker.lower() and i['liquidity'] > liquidity and i['lay'] < maxLay and checkDate(date, beforeDate) == True:
                        if i not in conversions:
                            conversions.append(i)
                else:
                    if i['bookmaker'].lower() == bookmaker.lower() and i['liquidity'] > liquidity and i['lay'] < maxLay:
                        if i not in conversions:
                            conversions.append(i)

            sorted_conversions = sorted(conversions, key=lambda x: x['rating'], reverse=True)
            value = ''
            for i in sorted_conversions[0:6]:
                sr = f"{i['rating']:.2f}"
                
                if i['source'] is None:
                    value += f"{i['event_name']}**,** {i['bet']}**,** {str(sr)}%**,** ${str(i['liquidity'])}**,** {str(i['back'])}/{str(i['lay'])}**,** {formatDate(i['date'])}**,** [Betfair]({i['betfair_source']})\n"
                else:
                    if bookmaker.lower() == 'bet365':
                        i['source'] = i['source'].replace('<STATE>', 'z1')
                    value += f"[{i['event_name']}]({i['source'].replace('au//', 'au/')})**,** {i['bet']}**,** {str(sr)}%**,** ${str(i['liquidity'])}**,** {str(i['back'])}/{str(i['lay'])}**,** {formatDate(i['date'])}**,** [Betfair]({i['betfair_source']})\n"

                value.replace('http://', 'https://\u200B').replace('<STATE>', 'z1')

            log(slug+'Successfully got SR conversions')    
            return value
        else:
            log(slug+'Error requesting conversions. Code: '+str(r.status_code))
            return 'Error requesting conversions. Code: '+str(r.status_code)
        
    except Exception as e:
        log(slug+'Error getting conversions. Error: '+str(e))
        return 'Error getting conversions. Error: '+str(e)



def login(session):
    slug = '[CONVERSIONS] : '
    try:
        log(slug+'Logging in...')
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://bonusbank.com.au',
            'priority': 'u=0, i',
            'referer': 'https://bonusbank.com.au/login/',
            'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        }

        data = {
            'log': config['username'],
            'pwd': config['password'],
            'rememberme': 'forever',
            'wp-submit': 'Log In',
            'redirect_to': 'https://bonusbank.com.au/post-login/',
            'mepr_process_login_form': 'true',
            'mepr_is_login_page': 'true',
        }

        try:
            r = session.post('https://bonusbank.com.au/login/', headers=headers, data=data)
        except:
            log(slug+'Failed to connect to bonus bank')  
            return False, 'Error connecting to site.'
        if r.status_code == 200:
            if r.url == 'https://bonusbank.com.au/dashboard/':
                log(slug+'Successfully logged in')
                return True, ''
            else:
                log(slug+'Error logging in')
                return False, 'Error logging in to site.'
        else:
            log(slug+'Error requesting conversions. Code: '+str(r.status_code)    )
            return 'Error requesting conversions. Code: '+str(r.status_code)    

    except Exception as e:
        log(slug+'Error getting conversions. Error: '+str(e))
        return 'Error getting conversions. Error: '+str(e)



def getNonce(session):
    slug = '[CONVERSIONS] : '
    try:
        log(slug+'Getting nonce...')
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'priority': 'u=0, i',
            'referer': 'https://bonusbank.com.au/dashboard/',
            'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        }
        try:
            r = session.get('https://bonusbank.com.au/matched-betting-software/', headers=headers)
        except:
            log(slug+'Failed to connect to bonus bank')  
            return 'Error connecting to site.'
        if r.status_code == 200:
            try:
                log(slug+'Successfully got nonce')
                return r.text.split('handle-vars-js-after')[1].split('window.nonce = "')[1].split('"')[0]
            except Exception as e:
                log(slug+'Error getting conversions. Error: '+str(e))
                return 'Error getting conversions. Error: '+str(e)
        else:
            log(slug+'Error requesting conversions. Code: '+str(r.status_code))
            return 'Error requesting conversions. Code: '+str(r.status_code)
    except Exception as e:
        log(slug+'Error getting conversions. Error: '+str(e))
        return 'Error getting conversions. Error: '+str(e)



def checkUsed(liquidity, max_lay, before_date):
    string = ''
    if liquidity != 0.00:
        string += f'over **AUD${str(liquidity)}** liquidity'

    if max_lay != 999999.99:
        if len(string) != 0:
            string+= ' and '
        string+= f'under **{str(max_lay)}** lay odds'

    if len(string) != 0:
        string = 'with ' + string
    
    if before_date != '':
        if len(string) != 0:
            string+= ' and '
        string+= f'before **{before_date}**'

    return string



@bot.tree.command(name="get_snr", description = "Get top SNR conversions matching parameters")
@app_commands.describe(bookmaker="Bookie name", liquidity='Minimum liquidity in $AUD', max_lay="Maximum lay odds", before_date="Before date (e.g. 29/04)")
@app_commands.choices(bookmaker=bookmaker_choices)
async def get_snr(interaction: discord.Interaction, bookmaker: str, liquidity: float = 0.00, max_lay: float = 999999.99, before_date: str = ''):
    slug = f'[{interaction.guild}] [{interaction.user.name}] : '
    log(slug+"Used the get snr command for {}".format(bookmaker))
    if interaction.channel.name == 'conversions' or interaction.channel.name == 'mb-conversions':
        if bookmaker.lower() in bookmakers:
            session = requests.session()
            await interaction.response.defer()
            if before_date != None:
                before_date = formatDate1(before_date)
            conversions = getConversions(bookmaker, session, liquidity, max_lay, before_date)
            if 'Error' not in conversions:
                if len(conversions) != 0:
                    msg = '**'+bookmaker.title()+f' SNR Conversions**\n\nTop 6 conversions '+checkUsed(liquidity, max_lay, before_date)+'\n\n__**Game, Result, Rating, Liquidity, Back/Lay, Date**__\n'+conversions
                    await interaction.followup.send(msg)
                    log(slug+"Sent conversions")
                else:
                    log(slug+"There are no conversions for specified parameters")
                    await interaction.followup.send(f"{interaction.user.name} there are no conversions for your specified parameters.", ephemeral=True)
            else:
                log(slug+"There was an error. Error: "+conversions)
                await interaction.followup.send(f"{interaction.user.name} there was an error please try again. Error: "+conversions, ephemeral=True)
        else:
            log(slug+'Unknown bookmaker: '+bookmaker)
            await interaction.response.send_message(f"{interaction.user.name} I do not know that bookmaker. Please see /conversions_help for all available bookmakers.", ephemeral=True)
    else:
        log(slug+'Used in wrong channel')
        if interaction.guild.name == 'Unity':
            await interaction.response.send_message(f"{interaction.user.name} please use this command in the [#conversions](https://discord.com/channels/1157952859988566016/1158671262747463680) channel.", ephemeral=True)
        else:
            await interaction.response.send_message(f"{interaction.user.name} please use this command in the [#mb-conversions](https://discord.com/channels/727765154309341185/1286235797762215937) channel.", ephemeral=True)



@bot.tree.command(name="get_sr", description = "Get top SR conversions matching parameters")
@app_commands.describe(bookmaker="Bookie name", liquidity='Minimum liquidity in $AUD', max_lay="Maximum lay odds", before_date="Before date (e.g. 29/04)")
@app_commands.choices(bookmaker=bookmaker_choices)
async def get_conversions(interaction: discord.Interaction, bookmaker: str, liquidity: float = 0.00, max_lay: float = 999999.99, before_date: str = ''):
    slug = f'[{interaction.guild}] [{interaction.user.name}] : '
    log(slug+"Used the get sr command for {}".format(bookmaker))
    if interaction.channel.name == 'conversions' or interaction.channel.name == 'mb-conversions':
        if bookmaker.lower() in bookmakers:
            session = requests.session()
            await interaction.response.defer()
            if before_date != None:
                before_date = formatDate1(before_date)
            conversions = getSR(bookmaker, session, liquidity, max_lay, before_date)
            if 'Error' not in conversions:
                if len(conversions) != 0:
                    msg = '**'+bookmaker.title()+f' SR Conversions**\n\nTop 6 conversions '+checkUsed(liquidity, max_lay, before_date)+'\n\n__**Game, Result, Rating, Liquidity, Back/Lay, Date**__\n'+conversions
                    await interaction.followup.send(msg)
                    log(slug+"Sent conversions")
                else:
                    log(slug+"There are no conversions for specified parameters")
                    await interaction.followup.send(f"{interaction.user.name} there are no conversions for your specified parameters.", ephemeral=True)
            else:
                log(slug+"There was an error. Error: "+conversions)
                await interaction.followup.send(f"{interaction.user.name} there was an error please try again. Error: "+conversions, ephemeral=True)
        else:
            log(slug+'Unknown bookmaker: '+bookmaker)
            await interaction.response.send_message(f"{interaction.user.name} I do not know that bookmaker. Please see /conversions_help for all available bookmakers.", ephemeral=True)
    else:
        log(slug+'Used in wrong channel')
        if interaction.guild.name == 'Unity':
            await interaction.response.send_message(f"{interaction.user.name} please use this command in the [#conversions](https://discord.com/channels/1157952859988566016/1158671262747463680) channel.", ephemeral=True)
        else:
            await interaction.response.send_message(f"{interaction.user.name} please use this command in the [#mb-conversions](https://discord.com/channels/727765154309341185/1286235797762215937) channel.", ephemeral=True)



@bot.tree.command(name="conversions_help",description = "Help with conversions")
async def conversions_help(interaction: discord.Interaction):
    slug = f'[{interaction.guild}] [{interaction.user.name}] : '
    log(slug+"Used the conversions help command")
    await interaction.response.send_message(f"{interaction.user.name} to get conversions do the command /get_conversions and fill out the information asked.\n\n__**Available bookmakers are:**__ \n"+'\n'.join([bookmaker.title() for bookmaker in bookmakers]), ephemeral=True)



@bot.tree.command(name="calculate_snr", description = "Calculate your lay and liability for bonus bets")
@app_commands.choices(currency=currency_choices)
@app_commands.describe(stake="Bonus Bet Amount", back='Back Odds', lay="Lay Odds", currency='Currency your bonus bet is in', commission="Betfair commission % [Default: 6]")
async def calculate_snr(interaction: discord.Interaction, stake: float, back: float, lay: float, currency: str = 'AUD', commission: int = 6):
    slug = f'[{interaction.guild}] [{interaction.user.name}] : '
    log(slug+"Used the calculate snr command")
    currency = currency.upper()
    commission = commission / 100.0
    originalStake = stake

    if currency == 'NZD':
        stake = stake * exchangeRateNZDAUD

    layAmount = (back - 1) / (lay - commission) * stake
    totalProfit = layAmount * (1-commission)
    stakeWin = originalStake * (back - 1)
    liability = (lay - 1) * layAmount
    
    rating = (totalProfit / stake) * 100
    
    if currency == 'NZD':
        totalProfitNZD = totalProfit * exchangeRateAUDNZD
        totalProfitNZD = f"{totalProfitNZD:.2f}"
        liabilityNZD = liability * exchangeRateAUDNZD
        liabilityNZD = f"{liabilityNZD:.2f}"

    layAmount = f"{layAmount:.2f}"
    totalProfit = f"{totalProfit:.2f}"
    liability = f"{liability:.2f}"
    rating = f"{rating:.2f}"
    stakeWin = f"{stakeWin:.2f}"

    if currency == 'NZD':
        await interaction.response.send_message(f"{interaction.user.name} you should lay **AUD${str(layAmount)}** at odds of **{str(lay)}** and your liability will be **AUD${str(liability)}** / **NZD${str(liabilityNZD)}**.\n\nYou should stake your **{currency}${str(originalStake)}** bonus bet at odds of **{str(back)}** to win **{currency}${str(stakeWin)}**.\n\nYour profit will be **AUD${str(totalProfit)}** / **NZD${str(totalProfitNZD)}** with a rating of **{str(rating)}%**.", ephemeral=True)
    else:
        await interaction.response.send_message(f"{interaction.user.name} you should lay **AUD${str(layAmount)}** at odds of **{str(lay)}** and your liability will be **AUD${str(liability)}**.\n\nYou should stake your **{currency}${str(originalStake)}** bonus bet at odds of **{str(back)}** to win **{currency}${str(stakeWin)}**.\n\nYour profit will be **AUD${str(totalProfit)}** with a rating of **{str(rating)}%**.", ephemeral=True)



def getType(rating):
    if "-" in str(rating):
        return "losing"
    
    return "winning"



@bot.tree.command(name="calculate_sr", description = "Calculate your lay and liability for mugging")
@app_commands.choices(currency=currency_choices)
@app_commands.describe(stake="Bet Amount", back='Back Odds', lay="Lay Odds", currency='Currency your bonus bet is in', commission="Betfair commission % [Default: 6%]")
async def calculate_sr(interaction: discord.Interaction, stake: float, back: float, lay: float, currency: str = 'AUD', commission: int = 6):
    slug = f'[{interaction.guild}] [{interaction.user.name}] : '
    log(slug+"Used the calculate sr command")
    currency = currency.upper()
    commission = commission / 100.0
    originalStake = stake
    if currency == 'NZD':
        stake = stake * exchangeRateNZDAUD  

    layAmount = (back * stake) / (lay - commission)
    liability = layAmount * (lay - 1)
    betReturn = originalStake * back
    totalReturn = ((1 - commission) * layAmount)
    netReturn = totalReturn - stake

    rating = (totalReturn / stake) * 100
    
    if currency == 'NZD':
        totalReturnNZD = totalReturn * exchangeRateAUDNZD
        totalReturnNZD = f"{totalReturnNZD:.2f}"
        netReturnNZD = netReturn * exchangeRateAUDNZD
        netReturnNZD = f"{netReturnNZD:.2f}"
        liabilityNZD = liability * exchangeRateAUDNZD
        liabilityNZD = f"{liabilityNZD:.2f}"
    
    rating = f"{rating:.2f}"
    layAmount = f"{layAmount:.2f}"
    totalReturn = f"{totalReturn:.2f}"
    netReturn = f"{netReturn:.2f}"
    liability = f"{liability:.2f}"
    
    if currency == 'NZD':
        await interaction.response.send_message(f"{interaction.user.name} you should lay **AUD${str(layAmount)}** at odds of **{str(lay)}** and your liability will be **AUD${str(liability)}** / **NZD${str(liabilityNZD)}**.\n\nYou should stake your **{currency}${str(originalStake)}** bet at odds of **{str(back)}** to return **{currency}${str(betReturn)}**.\n\nYour net return will be **AUD${str(netReturn)}** / **NZD${str(netReturnNZD)}** with a rating of **{str(rating)}%**.", ephemeral=True)
    else:
        await interaction.response.send_message(f"{interaction.user.name} you should lay **AUD${str(layAmount)}** at odds of **{str(lay)}** and your liability will be **AUD${str(liability)}**.\n\nYou should stake your **{currency}${str(originalStake)}** bet at odds of **{str(back)}** to return **{currency}${str(betReturn)}**.\n\nYour net return will be **AUD${str(netReturn)}** with a rating of **{str(rating)}%**.", ephemeral=True)



def calculate_sr_max_liquidity(liquidity, back, lay, slug, currency='AUD', commission=0.06):

    try:
        log(slug+'Calculating maximum stake for liquidity: AUD$' + str(liquidity))
        
        max_stake_aud = liquidity * (lay - commission) / back
        
        if currency == 'NZD':
            max_stake = max_stake_aud * exchangeRateAUDNZD
        else:
            max_stake = max_stake_aud
        
        log(slug+'Maximum stake calculated: ' + currency + '$' + str(round(max_stake, 2)))
        return max_stake
        
    except Exception as e:
        log(slug+'Error calculating maximum stake. Error: ' + str(e))
        log(slug+'Traceback: {}'.format(traceback.format_exc()))
        return 0
    


@bot.tree.command(name="calculate_sr_liquidity", description="Calculate maximum SR stake given your available liquidity")
@app_commands.choices(currency=currency_choices)
@app_commands.describe(liquidity="Available liquidity amount in AUD", back='Back Odds', lay="Lay Odds", currency='Currency your bet is in', commission="Betfair commission % [Default: 6]")
async def calculate_sr_liquidity(interaction: discord.Interaction, liquidity: float, back: float, lay: float, currency: str = 'AUD', commission: int = 6):
    slug = f'[{interaction.guild}] [{interaction.user.name}] : '
    log(slug+"Used the calculate_sr_liquidity command")
    
    currency = currency.upper()
    commission_decimal = commission / 100.0
    
    max_stake = calculate_sr_max_liquidity(liquidity, back, lay, slug, currency, commission_decimal)
    
    max_stake_aud = max_stake
    if currency == 'NZD':
        max_stake_aud = max_stake * exchangeRateNZDAUD
    
    layAmount = (back * max_stake_aud) / (lay - commission_decimal)
    betReturn = max_stake * back
    totalReturn = (1 - commission_decimal) * layAmount
    netReturn = totalReturn - max_stake_aud
    
    max_stake_formatted = f"{max_stake:.2f}"
    betReturn_formatted = f"{betReturn:.2f}"
    netReturn_formatted = f"{netReturn:.2f}"
    liquidity_formatted = f"{liquidity:.2f}"
    rating = f"{(totalReturn / max_stake_aud) * 100:.2f}"
    
    if currency == 'NZD':
        netReturnNZD = netReturn * exchangeRateAUDNZD
        await interaction.response.send_message(
            f"{interaction.user.name} with **AUD${liquidity_formatted}** liquidity, you can stake a maximum of **{currency}${max_stake_formatted}** on a regular bet at odds of **{str(back)}**.\n\n"
            f"This would return **{currency}${betReturn_formatted}** if successful with a net profit of **AUD${netReturn_formatted}** / **NZD${netReturnNZD:.2f}** and a rating of **{rating}%**.", 
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"{interaction.user.name} with **AUD${liquidity_formatted}** liquidity, you can stake a maximum of **{currency}${max_stake_formatted}** on a regular bet at odds of **{str(back)}**.\n\n"
            f"This would return **{currency}${betReturn_formatted}** if successful with a net profit of **AUD${netReturn_formatted}** and a rating of **{rating}%**.", 
            ephemeral=True
        )



def calculate_snr_max_liquidity(liquidity, back, lay, slug, currency='AUD', commission=0.06):

    try:
        log(slug+'Calculating maximum stake for liquidity: AUD$' + str(liquidity))

        layFactor = (back - 1) / (lay - commission)
        max_stake_aud = liquidity / layFactor
        
        if currency == 'NZD':
            max_stake = max_stake_aud * exchangeRateAUDNZD
        else:
            max_stake = max_stake_aud
        
        log(slug+'Maximum stake calculated: ' + currency + '$' + str(round(max_stake, 2)))
        return max_stake
        
    except Exception as e:
        log(slug+'Error calculating maximum stake. Error: ' + str(e))
        log(slug+'Traceback: {}'.format(traceback.format_exc()))
        return 0
    


@bot.tree.command(name="calculate_snr_liquidity", description="Calculate maximum stake given your available liquidity")
@app_commands.choices(currency=currency_choices)
@app_commands.describe(liquidity="Available liquidity amount in AUD", back='Back Odds', lay="Lay Odds", currency='Currency your bonus bet will be in', commission="Betfair commission % [Default: 6]")
async def calculate_snr_liquidity(interaction: discord.Interaction, liquidity: float, back: float, lay: float, currency: str = 'AUD', commission: int = 6):
    slug = f'[{interaction.guild}] [{interaction.user.name}] : '
    log(slug+"Used the calculate_snr_liquidity command")
    
    currency = currency.upper()
    commission_decimal = commission / 100.0
    
    max_stake = calculate_snr_max_liquidity(liquidity, back, lay, slug, currency, commission_decimal)
    
    max_stake_aud = max_stake
    if currency == 'NZD':
        max_stake_aud = max_stake * exchangeRateNZDAUD
    
    layAmount = (back - 1) / (lay - commission_decimal) * max_stake_aud
    totalProfit = layAmount * (1-commission_decimal)
    stakeWin = max_stake * (back - 1)

    max_stake_formatted = f"{max_stake:.2f}"
    totalProfit_formatted = f"{totalProfit:.2f}"
    liquidity_formatted = f"{liquidity:.2f}"
    stakeWin_formatted = f"{stakeWin:.2f}"
    rating = f"{(totalProfit / max_stake_aud) * 100:.2f}"
    
    if currency == 'NZD':
        totalProfitNZD = totalProfit * exchangeRateAUDNZD
        await interaction.response.send_message(
            f"{interaction.user.name} with **AUD${liquidity_formatted}** liquidity, you can stake a maximum of **{currency}${max_stake_formatted}** on a bonus bet at odds of **{str(back)}**.\n\n"
            f"This would win **{currency}${stakeWin_formatted}** if successful with a profit of **AUD${totalProfit_formatted}** / **NZD${totalProfitNZD:.2f}** and a rating of **{rating}%**.", 
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"{interaction.user.name} with **AUD${liquidity_formatted}** liquidity, you can stake a maximum of **{currency}${max_stake_formatted}** on a bonus bet at odds of **{str(back)}**.\n\n"
            f"This would win **{currency}${stakeWin_formatted}** if successful with a profit of **AUD${totalProfit_formatted}** and a rating of **{rating}%**.", 
            ephemeral=True
        )




exchangeRateAUDNZD = None
exchangeRateAUDNZD = None


def updateExchangeRates():
    global exchangeRateNZDAUD, exchangeRateAUDNZD

    try:
        r = requests.get("https://api.currencyapi.com/v3/latest?base_currency=NZD", headers=currencyHeaders)
        exchangeRateNZDAUD = r.json()['data']['AUD']['value']
    except:
        log('Failed to update NZD -> AUD value')

    try:
        r = requests.get("https://api.currencyapi.com/v3/latest?base_currency=AUD", headers=currencyHeaders)
        exchangeRateAUDNZD = r.json()['data']['NZD']['value']
    except:
        log('Failed to update AUD -> NZD value')

    sleep(43200) # half a day


@bot.event
async def on_ready():
    log("Bot is running")
    try:
        synced = await bot.tree.sync()
        log(f"Synced {len(synced)} command(s)")
    except Exception as e:
        log(e)


def load_config(path='config.json'):
    """Load and return JSON config as a dict."""
    with open(path, 'r') as f:
        return json.load(f)

config = load_config

currencyHeaders = {"apikey": config['currencyAPI']}


threading.Thread(target=updateExchangeRates, daemon=True).start()
sleep(5)

bot.run(config['discordBotToken'])


