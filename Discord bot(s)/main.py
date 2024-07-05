
'''
Remaining to-do list:

- Add more games
- Add a time limit
'''

import os

from  discord import Intents, Client, Message, Member, Embed, Color
from dotenv import load_dotenv
from random import choice, randint
import asyncio
from random import choice, randint

#Load token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#bot setup: activate permissions
intents: Intents = Intents.default()
intents.message_content = True 
client: Client = Client(intents=intents)

#keeping track of the ongoing games
ongoing_games = {}

#message functionality

#Deals with the user inputs
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('Message empty, some error')
        return
    
    mentioned_member = None
    if message.mentions:
        mentioned_member = message.mentions[0]

    if message.author.id in ongoing_games:
        await handle_games(message, user_message)
        return
    

    if botmsg:= user_message[0] == '=':
        user_message = user_message[1:]


    
    try:
        if botmsg:
            try:
                info_dict[message.author.id]
            except:
                await create_pfp(message)
            else:
                if user_message.lower().startswith('g'):
                    await gamble(message, user_message, mentioned_member)   
                elif user_message.lower().startswith('pay loan'):
                    await pay_loan(message)
                elif user_message.startswith('p'):
                    await check_profile(message, mentioned_member)
                elif  user_message.lower().startswith('loan'):
                    await loan(message)
                elif user_message.lower().startswith('save'):
                    await saveinfo()
                    print('SAVED INFO SO FAR')
                elif user_message.lower().startswith('info'):
                    embed = get_info()
                    await message.channel.send(embed=embed)
                else:
                    response = get_response(user_message)
                    await message.channel.send(response) 
    except Exception as e:
        print(f'Error: {e}')


#Creates a profile for the user and allows them to use the bot further
async def create_pfp(message):
    await message.channel.send('Welcome to the gambling bot. Use =info to learn the commands. Here is your profile:') 
    await check_profile(message, None)
    return

#Gets info for =info
def get_info():
    embed = Embed(
        title= 'Information',
        description= 'List of available commands',
        #color = Color.blue()
    )
    embed.add_field(name="=p", value="Checks the user's profile", inline=False)
    embed.add_field(name="=g", value="Allows you to gamble with various games", inline=False)
    embed.add_field(name="=loan", value="Allows the user to take a loan out to get some money.", inline=False)
    embed.add_field(name="=pay loan", value="Allows the user to pay off loans", inline=False)
    embed.set_footer(text="Use =save to save info, or when the bot closes, everything is gone.")
    return embed 

#Handles the text based responses with no additional followup
def get_response(user_input:str) -> str:
    lowered: str = user_input.lower()

    if lowered == '':
        return 'Use =info for more'
    elif 'hello' in lowered:
        return 'hello'
    elif 'roll dice' in lowered:
        return f'you rolled: {randint(1,6)}'
    else:
        return 'This is not a valid command. Use =info for more information'

#Creates the games and makes sure they are valid
async def gamble(message: Message, userMessage: str, opp: Member) -> None:
    con = userMessage.lower().split(" ") 
    # returned con example: ["=g", "coinflip", "1000"]

    try:
        if con[1] == 'coinflip':
            if int(con[2]) > info_dict[message.author.id][0]:
                await message.channel.send('You do not have the funds for this gamble.')
                return
            elif int(con[2]) < 0:
                await message.channel.send('You cannot gamble negative cash.')
                return
            else:
                await message.channel.send(f'For ${con[2]}, heads or tails?')
                ongoing_games[message.author.id] = ['coinflip', int(con[2])]
                info_dict[message.author.id][0] -= int(con[2])
                return
        elif con[1] == 'blackjack':
            NotImplemented
        elif con[1] == '1v1':
            if opp == message.author:
                await message.channel.send('You cannot 1v1 yourself.')
                return
            elif int(con[3]) > info_dict[message.author.id][0]:
                await message.channel.send('You do not have the funds for this gamble.')
                return
            elif int(con[3]) > info_dict[opp.id][0]:
                await message.channel.send(f'<@{opp.id}> does not have the funds for this gamble.')
                return    
            elif int(con[3]) < 0:
                await message.channel.send('You cannot gamble negative cash.')
                return
            else:
                await begin_challenge(message, opp)
        else:
            await message.channel.send('Please pick one of the available games')
    except:
        embed = Embed(
            title= 'Gambling!',
            description= 'List of available games and their corresponding commands',
            #color = Color.blue()
        )
        embed.add_field(name="Coinflip", value="=g coinflip 100", inline=False)
        embed.add_field(name="1v1", value="=g 1v1 @user 100", inline=False)
        embed.set_footer(text="More games comming!")
        await message.channel.send(embed = embed)
        return
        
#Handles the games after they have already been created
async def handle_games(message: Message, user_message: str) -> None:
    if ongoing_games[message.author.id][0] == 'coinflip':
        random = randint(0, 1)
        if random == 0:
            winner = 'tails'
        else:
            winner = 'heads'

        if user_message.lower() == 'heads' or user_message.lower() == 'tails':
            await message.channel.send(f'You picked {user_message.lower()}. Flipping the coin...')
            await asyncio.sleep(1)
            if winner == user_message.lower():
                await message.channel.send(f'It landed on {winner}! You won ${ongoing_games[message.author.id][1]}!')
                info_dict[message.author.id][0] += int(ongoing_games[message.author.id][1]) * 2
            else:
                await message.channel.send(f'It landed on {winner}... You lost your ${ongoing_games[message.author.id][1]}.')
            del ongoing_games[message.author.id]
        else:
            await message.channel.send('Not a valid choice, please try again and input either \'=heads\' or \'=tails\'.')
        return
    elif ongoing_games[message.author.id][0] == 'blackjack':
        NotImplemented
        return
    elif ongoing_games[message.author.id][0] == '1v1': 
        opp = ongoing_games[message.author.id][1]

        try:                    #make sure they are both involved in the game
            ongoing_games[opp.id]
        except:
            del ongoing_games[message.author.id]
            return
        
        if ongoing_games[message.author.id][2]: #if it's a 1v1 AND its the person's turn
            if ongoing_games[message.author.id][5] == 0: #if it's the first turn / game hasn't started yet
                if user_message.lower() == 'n':
                    await message.channel.send('Game has been denied. It is now terminated.')
                    del ongoing_games[message.author.id]
                    del ongoing_games[opp.id]
                elif user_message.lower() == 'y':
                    await message.channel.send(f'Game has been accepted. It is now <@{opp.id}>\'s turn. Pick a number between 0 - 100 and attempt to get the correct number!')
                    ongoing_games[message.author.id][5] += 1
                    ongoing_games[opp.id][5] += 1
                    ongoing_games[message.author.id][2] = not ongoing_games[message.author.id][2] #it's the other persons turn now
                    ongoing_games[opp.id][2] = not ongoing_games[opp.id][2]
                    print(info_dict[message.author.id][0])
                    print(info_dict[opp.id][0])
                    info_dict[message.author.id][0] -= int(ongoing_games[message.author.id][4])
                    info_dict[opp.id][0] -= int(ongoing_games[message.author.id][4])
                    print(info_dict[message.author.id][0])
                    print(info_dict[opp.id][0])
            else:
                if not is_number(user_message):
                    await message.channel.send('Not a valid input. Please input a number from 0-100')
                else:
                    try:
                        guessed_number = float(user_message)
                    except:
                        await message.channel.send('Input a valid value')
                        return
                    if guessed_number == ongoing_games[message.author.id][3]:
                        #All the stuff with winning
                        await message.channel.send(f'<@{message.author.id}> has guessed the correct number and beat <@{opp.id}>! They won ${ongoing_games[message.author.id][4]}! Congrats! :tada: :tada: :tada: ')
                        info_dict[message.author.id][0] += int(ongoing_games[message.author.id][4]) * 2 #Gives the person the money they won
                        info_dict[message.author.id][1] += 1
                        info_dict[opp.id][2] += 1
                        del ongoing_games[message.author.id]
                        del ongoing_games[opp.id]
                    elif guessed_number < ongoing_games[message.author.id][3]:
                        await message.channel.send(f'The correct number is **higher**')
                        ongoing_games[message.author.id][5] += 1
                        ongoing_games[opp.id][5] += 1
                        ongoing_games[message.author.id][2] = not ongoing_games[message.author.id][2] #it's the other persons turn now
                        ongoing_games[opp.id][2] = not ongoing_games[opp.id][2]     
                    elif guessed_number > ongoing_games[message.author.id][3]:
                        await message.channel.send(f'The correct number is **lower**')
                        ongoing_games[message.author.id][5] += 1
                        ongoing_games[opp.id][5] += 1
                        ongoing_games[message.author.id][2] = not ongoing_games[message.author.id][2] #it's the other persons turn now
                        ongoing_games[opp.id][2] = not ongoing_games[opp.id][2] 
        else: #if it's not the person's turn
            if user_message == 'stop':
                NotImplemented
            else:
                await message.channel.send('It\'s not your turn.')    
    else:
        await message.channel.send('Something went wrong, should never get to this point')
    return


#Creates teh challenge game 
async def begin_challenge(message: Message, opp: Member) -> None:
    await message.channel.send(f'<@{message.author.id}> would like to challenge <@{opp.id}> to a one-on-one! Y/N')
    correct_ans = randint(0, 100)
    amount_bet = message.content.lower().split()[3]
    ongoing_games[message.author.id] = ['1v1', opp, False, correct_ans, amount_bet, 0] #[‘1v1 challengee’  (opp),   (whose turn), (correct #), (amount bet), turn ]
    ongoing_games[opp.id] = ['1v1', message.author, True, correct_ans, amount_bet, 0]
    return

#check profile
async def check_profile(ctx, member: Member = None):
    if member == None: #if not @'ing someone, will be own profile
        member = ctx.author

    embed = Embed(title=f'{member.name}\'s profile')

    if member.id in info_dict:
        money, wins, losses, loans = info_dict[member.id]
        if wins + losses > 0:
            winrate = wins / (wins + losses) * 100
        else:
            winrate = '-'
    else: 
        #add the user_ID to the csv file
        info_dict[member.id] = [0, 0, 0, 0]
        money, wins, losses, loans, winrate = 0,0,0, 0,'-'


    if member.avatar:
        # Check if the member has a custom avatar
        embed.set_thumbnail(url=member.avatar.url)
    else:
        # If the member has the default avatar, set a placeholder image
        embed.set_thumbnail(url="https://discord.com/assets/6debd47ed13483642cf09e832ed0bc1b.png")
    
    embed.add_field(name='Money:', value = f'${money}', inline = False)
    embed.add_field(name='Score:', value = f'{wins}W   {losses}L', inline=True)
    try:
        embed.add_field(name='Winrate:  ', value = f'{round(int(winrate), 2)}%', inline=True)
    except:
        embed.add_field(name='Winrate:  ', value = f'{winrate}%', inline=True)

    embed.add_field(name='Loans Taken:  ', value = f'{loans}', inline=False)


    await ctx.channel.send(embed=embed)

#To get a loan
async def  loan(ctx) -> None:
    member = ctx.author
    if member.id in info_dict:
        info_dict[member.id][3] += 1
        info_dict[member.id][0] += 1000
    else:
        info_dict[member.id] = [1000, 0, 0, 1]
    await ctx.channel.send(f'{member.name} has taken out a loan.')

#To pay a loan off
async def pay_loan(ctx) -> None:
    member = ctx.author
    if info_dict[member.id][3] < 1:
        await ctx.channel.send('No loans to pay back.')
    else:
        if info_dict[member.id][0] >= 1000:
            info_dict[member.id][3] -= 1
            info_dict[member.id][0] -= 1000
            await ctx.channel.send(f'You have payed off one of your loans. You have {info_dict[member.id][3]} remaining to pay.')
        else:
            await ctx.channel.send('You do not have the funds to pay back any of your loans. You are broke.')


#Is it a number or 
def is_number(n):
    try:
        float(n)
    except:
        return False
    else: 
        return True
    

#bot startup 

@client.event
async def on_ready() -> None:
    print(f'{client.user} has connected to Discord!')


#handling incoming messages
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return 

    username = str(message.author)
    user_message = message.content
    channel = str(message.channel)
    
    print(f'[{channel}] {username}: "{user_message}"')

    await send_message(message, user_message)

#Uses info from csv file as starting info
def load_info() -> dict:
    file = open('info.csv', 'r')
    info_dict = {} #key is user ID and value is a list of the info we need
    first_line = True
    for line in file:
        value = line.strip().split(',')
        if first_line:
            first_line = False
        else:
            user_id = int(value[0])
            money = int(value[1])
            wins = int(value[2])
            losses = int(value[3])
            loans = int(value[4])
            info_dict[user_id] = [money, wins, losses, loans]
    return info_dict

#Saves all info into the csv file
async def saveinfo() -> None:
    file = open('info.csv', 'w')
    file.write('Name,Money,Wins,Losses,Loans' + '\n')
    for key_ in info_dict:
        line = f'{key_},{info_dict[key_][0]},{info_dict[key_][1]},{info_dict[key_][2]},{info_dict[key_][3]}\n'
        file.write(line)
    return

#main entry point
def main() -> None:
    client.run(TOKEN)
    

info_dict = load_info() #will need the info globally
main()


