import json
import re

from pyrogram import Client, Filters
from pyrogram import (InlineKeyboardMarkup,
                      InlineKeyboardButton,
                      CallbackQuery)

import functions as func


from Config import Config

app = Client(
    api_id=Config.aid,
    api_hash=Config.ahash,
    bot_token=Config.bot_token,
    session_name='rotom-2.0'
)

texts = json.load(open('src/texts.json', 'r'))
data = json.load(open('src/pkmn.json', 'r'))
stats = json.load(open('src/stats.json', 'r'))
jtype = json.load(open('src/type.json', 'r'))

usage_dict = {'vgc': None}



# ===== Stats =====
@app.on_message(Filters.private & Filters.create(lambda _, message: str(message.chat.id) not in stats['users']))
@app.on_message(Filters.group & Filters.create(lambda _, message: str(message.chat.id) not in stats['groups']))
def get_bot_data(app, message):
    cid = str(message.chat.id)
    if message.chat.type == 'private':
        stats['users'][cid] = {}
        name = message.chat.first_name
        try:
            name = message.chat.first_name + ' ' + message.chat.last_name
        except TypeError:
            name = message.chat.first_name
        stats['users'][cid]['name'] = name
        try:
            stats['users'][cid]['username'] = message.chat.username
        except AttributeError:
            pass

    elif message.chat.type in ['group', 'supergroup']:
        stats['groups'][cid] = {}
        stats['groups'][cid]['title'] = message.chat.title
        try:
            stats['groups'][cid]['username'] = message.chat.username
        except AttributeError:
            pass
        stats['groups'][cid]['members'] = app.get_chat(cid).members_count

    json.dump(stats, open('src/stats.json', 'w'), indent=4)
    print(stats)
    print('\n\n')
    message.continue_propagation()


@app.on_message(Filters.command(['stats', 'stats@officerjennyprobot']))
def get_stats(app, message):
    if message.from_user.id in Config.sudo:
        members = 0
        for group in stats['groups']:
            members += stats['groups'][group]['members']
        text = texts['stats'].format(
            len(stats['users']),
            len(stats['groups']),
            members
        )
        app.send_message(
            chat_id=message.chat.id,
            text=text
        )


# ===== Home =====
@app.on_message(Filters.command(['start', 'start@officerjennyprobot']))
def start(app, message):
    app.send_message(
        chat_id=message.chat.id,
        text=texts['start_message'],
        parse_mode='HTML'
    )

# ==== Type Pokemon =====
@app.on_message(Filters.command(['type', 'type@officerjennyprobot']))
def ptype(app, message):
    try:
        gtype = message.text.split(' ')[1]
    except IndexError as s:
        app.send_message(
            chat_id=message.chat.id,
            text="`Syntex error: use eg '/type fairy'`"
        )
        return
    try:
        data = jtype[gtype.lower()]
    except KeyError as s:
        app.send_message(
            chat_id=message.chat.id,
            text=("`Eeeh, Lol, This type doesn't exists :/ `\n"
                  "`Do  /types  to check for the existing types.`")
        )
        return
    strong_against = ", ".join(data['strong_against'])
    weak_against = ", ".join(data['weak_against'])
    resistant_to = ", ".join(data['resistant_to'])
    vulnerable_to = ", ".join(data['vulnerable_to'])
    keyboard = ([[
        InlineKeyboardButton('All Types',callback_data=f"hexa_back_{message.from_user.id}")]])
    app.send_message(
        chat_id=message.chat.id,
        text=(f"Type  :  `{gtype.lower()}`\n\n"
              f"Strong Against:\n`{strong_against}`\n\n"
              f"Weak Against:\n`{weak_against}`\n\n"
              f"Resistant To:\n`{resistant_to}`\n\n"
              f"Vulnerable To:\n`{vulnerable_to}`"),
        reply_markup=InlineKeyboardMarkup(keyboard)
           
    )

# ==== Types List =====
def ptype_buttons(user_id):
    keyboard = ([[
        InlineKeyboardButton('Normal',callback_data=f"type_normal_{user_id}"),
        InlineKeyboardButton('Fighting',callback_data=f"type_fighting_{user_id}"),
        InlineKeyboardButton('Flying',callback_data=f"type_flying_{user_id}")]])
    keyboard += ([[
        InlineKeyboardButton('Poison',callback_data=f"type_poison_{user_id}"),
        InlineKeyboardButton('Ground',callback_data=f"type_ground_{user_id}"),
        InlineKeyboardButton('Rock',callback_data=f"type_rock_{user_id}")]])
    keyboard += ([[
        InlineKeyboardButton('Bug',callback_data=f"type_bug_{user_id}"),
        InlineKeyboardButton('Ghost',callback_data=f"type_ghost_{user_id}"),
        InlineKeyboardButton('Steel',callback_data=f"type_steel_{user_id}")]])
    keyboard += ([[
        InlineKeyboardButton('Fire',callback_data=f"type_fire_{user_id}"),
        InlineKeyboardButton('Water',callback_data=f"type_water_{user_id}"),
        InlineKeyboardButton('Grass',callback_data=f"type_grass_{user_id}")]])
    keyboard += ([[
        InlineKeyboardButton('Electric',callback_data=f"type_electric_{user_id}"),
        InlineKeyboardButton('Psychic',callback_data=f"type_psychic_{user_id}"),
        InlineKeyboardButton('Ice',callback_data=f"type_ice_{user_id}")]])
    keyboard += ([[
        InlineKeyboardButton('Dragon',callback_data=f"type_dragon_{user_id}"),
        InlineKeyboardButton('Fairy',callback_data=f"type_fairy_{user_id}"),
        InlineKeyboardButton('Dark',callback_data=f"type_dark_{user_id}")]])
    keyboard += ([[
        InlineKeyboardButton('Delete',callback_data=f"hexa_delete_{user_id}")]])
    return keyboard
    
@app.on_message(Filters.command(['types', 'types@officerjennyprobot']))
def types(app, message): 
    user_id = message.from_user.id
    app.send_message(
        chat_id=message.chat.id,
        text="List of types of Pokemons:",
        reply_markup=InlineKeyboardMarkup(ptype_buttons(user_id))
    )

# ===== Types Callback ====
@app.on_callback_query(Filters.create(lambda _, query: 'type_' in query.data))
def button(client: app, callback_query: CallbackQuery):
    q_data = callback_query.data
    query_data = q_data.split('_')[0]
    type_n = q_data.split('_')[1]
    user_id = int(q_data.split('_')[2])
    cuser_id = callback_query.from_user.id
    if cuser_id == user_id:
        if query_data == "type":
            data = jtype[type_n]
            strong_against = ", ".join(data['strong_against'])
            weak_against = ", ".join(data['weak_against'])
            resistant_to = ", ".join(data['resistant_to'])
            vulnerable_to = ", ".join(data['vulnerable_to'])
            keyboard = ([[
            InlineKeyboardButton('Back',callback_data=f"hexa_back_{user_id}")]])
            callback_query.message.edit_text(
                text=(f"Type  :  `{type_n}`\n\n"
                f"Strong Against:\n`{strong_against}`\n\n"
                f"Weak Against:\n`{weak_against}`\n\n"
                f"Resistant To:\n`{resistant_to}`\n\n"
                f"Vulnerable To:\n`{vulnerable_to}`"),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    else:
        callback_query.answer(
            text="You can't use this button!",
            show_alert=True
        )
    

@app.on_callback_query(Filters.create(lambda _, query: 'hexa_' in query.data))
def button2(client: app, callback_query: CallbackQuery):
    q_data = callback_query.data
    query_data = q_data.split('_')[1]
    user_id = int(q_data.split('_')[2])
    cuser_id = callback_query.from_user.id
    if user_id == cuser_id:
        if query_data == "back":
            callback_query.message.edit_text(
                "List of types of Pokemons:",
                reply_markup=InlineKeyboardMarkup(ptype_buttons(user_id))
            )
        elif query_data == "delete":
            callback_query.message.delete()
        else:
            return
    else:
        callback_query.answer(
            text="You can't use this button!",
            show_alert=True
        )
  
# ===== Pokemon Type Command ======
@app.on_message(Filters.command(['ptype', 'ptype@officerjennyprobot']))
def poketypes(app, message): 
    user_id = message.from_user.id
    try:
        arg = message.text.split(' ')[1].lower()
    except IndexError:
        app.send_message(
            chat_id=message.chat.id,
            text=("`Syntex error: use eg '/ptype pokemon_name'`\n"
                  "`eg /ptype Lunala`")
        )
        return  
    try:
        p_type = data[arg][arg]['type']
    except KeyError:
        app.send_message(
            chat_id=message.chat.id,
            text="`Eeeh, Lol, This pokemon doesn't exists :/`"
        )
        return
    
    try:
        get_pt = f"{p_type['type1']}, {p_type['type2']:}"
        keyboard = ([[
        InlineKeyboardButton(p_type['type1'],callback_data=f"poket_{p_type['type1']}_{arg}_{user_id}"),
        InlineKeyboardButton(p_type['type2'],callback_data=f"poket_{p_type['type2']}_{arg}_{user_id}")]])
    except KeyError:
        get_pt = f"{p_type['type1']}"
        keyboard = ([[
        InlineKeyboardButton(p_type['type1'],callback_data=f"poket_{p_type['type1']}_{arg}_{user_id}")]])
    app.send_message(
        chat_id=message.chat.id,
        text=(f"Pokemon: `{arg}`\n\n"
              f"Types: `{get_pt}`\n\n"
              "__Click the button below to get info about the found type's/types' effectiveness!__"),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
@app.on_callback_query(Filters.create(lambda _, query: 'poket_' in query.data))
def poketypes_callback(client: app, callback_query: CallbackQuery):
    q_data = callback_query.data
    query_data = q_data.split('_')[1].lower()
    pt_name = q_data.split('_')[2]
    user_id = int(q_data.split('_')[3])  
    if callback_query.from_user.id == user_id:  
        data = jtype[query_data]
        strong_against = ", ".join(data['strong_against'])
        weak_against = ", ".join(data['weak_against'])
        resistant_to = ", ".join(data['resistant_to'])
        vulnerable_to = ", ".join(data['vulnerable_to'])
        keyboard = ([[
        InlineKeyboardButton('Back',callback_data=f"pback_{pt_name}_{user_id}")]])
        callback_query.message.edit_text(
            text=(f"Type  :  `{query_data}`\n\n"
            f"Strong Against:\n`{strong_against}`\n\n"
            f"Weak Against:\n`{weak_against}`\n\n"
            f"Resistant To:\n`{resistant_to}`\n\n"
            f"Vulnerable To:\n`{vulnerable_to}`"),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        callback_query.answer(
            text="You're not allowed to use this!",
            show_alert=True
        )
    
@app.on_callback_query(Filters.create(lambda _, query: 'pback_' in query.data))
def poketypes_back(client: app, callback_query: CallbackQuery):
    q_data = callback_query.data
    query_data = q_data.split('_')[1].lower()
    user_id = int(q_data.split('_')[2]) 
    if callback_query.from_user.id == user_id:
        p_type = data[query_data][query_data]['type']
        try:
            get_pt = f"{p_type['type1']}, {p_type['type2']:}"
            keyboard = ([[
            InlineKeyboardButton(p_type['type1'],callback_data=f"poket_{p_type['type1']}_{query_data}_{user_id}"),
            InlineKeyboardButton(p_type['type2'],callback_data=f"poket_{p_type['type2']}_{query_data}_{user_id}")]])
        except KeyError:
            get_pt = f"{p_type['type1']}"
            keyboard = ([[
            InlineKeyboardButton(p_type['type1'],callback_data=f"poket_{p_type['type1']}_{query_data}_{user_id}")]])
        callback_query.message.edit_text(
            (f"Pokemon: `{query_data}`\n\n"
             f"Types: `{get_pt}`\n\n"
             "__Click the button below to get info about the found type's/types' effectiveness!__"),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        callback_query.answer(
            text="You're not allowed to use this!",
            show_alert=True
        )
    
        
# ===== Data command =====
@app.on_callback_query(Filters.create(lambda _, query: 'basic_infos' in query.data))
@app.on_message(Filters.command(['data', 'data@officerjennyprobot']))
def pkmn_search(app, message):
    try:
        if message.text == '/data' or message.text == '/data@officerjennyprobot':
            app.send_message(message.chat.id, texts['error1'], parse_mode='HTML')
            return None
        pkmn = func.find_name(message.text)
        result = func.check_name(pkmn, data)

        if type(result) == str:
            app.send_message(message.chat.id, result)
            return None
        elif type(result) == list:
            best_matches(app, message, result)
            return None
        else:
            pkmn = result['pkmn']
            form = result['form']
    except AttributeError:
        pkmn = re.split('/', message.data)[1]
        form = re.split('/', message.data)[2]


    if pkmn in form:
        text = func.set_message(data[pkmn][form], reduced=True)
    else:
        base_form = re.sub('_', ' ', pkmn.title())
        name = base_form + ' (' + data[pkmn][form]['name'] + ')'
        text = func.set_message(data[pkmn][form], name, reduced=True)

    markup_list = [[
        InlineKeyboardButton(
            text='➕ Expand',
            callback_data='all_infos/'+pkmn+'/'+form
        )
    ],
    [
        InlineKeyboardButton(
            text='⚔️ Moveset',
            callback_data='moveset/'+pkmn+'/'+form
        ),
        InlineKeyboardButton(
            text='🏠 Locations',
            callback_data='locations/'+pkmn+'/'+form
        )
    ]]
    for alt_form in data[pkmn]:
        if alt_form != form:
            markup_list.append([
                InlineKeyboardButton(
                    text=data[pkmn][alt_form]['name'],
                    callback_data='basic_infos/'+pkmn+'/'+alt_form
                )
            ])
    markup = InlineKeyboardMarkup(markup_list)

    func.bot_action(app, message, text, markup)


def best_matches(app, message, result):
    text = texts['results']
    emoji_list = ['1️⃣', '2️⃣', '3️⃣']
    index = 0
    for dictt in result:
        pkmn = dictt['pkmn']
        form = dictt['form']
        percentage = dictt['percentage']
        form_name = data[pkmn][form]['name']
        name = func.form_name(pkmn.title(), form_name)
        text += '\n{} <b>{}</b> (<i>{}</i>)'.format(
            emoji_list[index],
            name,
            percentage
        )
        if index == 0:
            text += ' [<b>⭐️ Top result</b>]'
        index += 1
    app.send_message(message.chat.id, text, parse_mode='HTML')


@app.on_callback_query(Filters.create(lambda _, query: 'all_infos' in query.data))
def all_infos(app, call):
    pkmn = re.split('/', call.data)[1]
    form = re.split('/', call.data)[2]
    
    if pkmn in form:
        text = func.set_message(data[pkmn][form], reduced=False)
    else:
        base_form = re.sub('_', ' ', pkmn.title())
        name = base_form + ' (' + data[pkmn][form]['name'] + ')'
        text = func.set_message(data[pkmn][form], name, reduced=False)

    markup_list = [[
        InlineKeyboardButton(
            text='➖ Reduce',
            callback_data='basic_infos/'+pkmn+'/'+form
        )
    ],
    [
        InlineKeyboardButton(
            text='⚔️ Moveset',
            callback_data='moveset/'+pkmn+'/'+form
        ),
        InlineKeyboardButton(
            text='🏠 Locations',
            callback_data='locations/'+pkmn+'/'+form
        )
    ]]
    for alt_form in data[pkmn]:
        if alt_form != form:
            markup_list.append([
                InlineKeyboardButton(
                    text=data[pkmn][alt_form]['name'],
                    callback_data='basic_infos/'+pkmn+'/'+alt_form
                )
            ])
    markup = InlineKeyboardMarkup(markup_list)

    func.bot_action(app, call, text, markup)


@app.on_callback_query(Filters.create(lambda _, query: 'moveset' in query.data))
def moveset(app, call):
    pkmn = re.split('/', call.data)[1]
    form = re.split('/', call.data)[2]
    if len(re.split('/', call.data)) == 4:
        page = int(re.split('/', call.data)[3])
    else:
        page = 1
    dictt = func.set_moveset(pkmn, form, page)

    func.bot_action(app, call, dictt['text'], dictt['markup'])


@app.on_callback_query(Filters.create(lambda _, query: 'locations' in query.data))
def locations(app, call):
    pkmn = re.split('/', call.data)[1]
    form = re.split('/', call.data)[2]

    text = func.get_locations(data, pkmn)

    markup = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            text='⚔️ Moveset',
            callback_data='moveset/'+pkmn+'/'+form
        )
    ],
    [
        InlineKeyboardButton(
            text='🔙 Back to basic infos',
            callback_data='basic_infos/'+pkmn+'/'+form
        )
    ]])

    func.bot_action(app, call, text, markup)


# ===== Usage command =====
@app.on_callback_query(Filters.create(lambda _, query: 'usage' in query.data))
@app.on_message(Filters.command(['usage', 'usage@officerjennyprobot']))
def usage(app, message):
    try:
        page = int(re.split('/', message.data)[1])
        dictt = func.get_usage_vgc(int(page), usage_dict['vgc'])
    except AttributeError:
        page = 1
        text = '<i>Yeah! wi8, Connecting to Pokémon Showdown database...</i>'
        message = app.send_message(message.chat.id, text, parse_mode='HTML')
        dictt = func.get_usage_vgc(int(page))
        usage_dict['vgc'] = dictt['vgc_usage']

    leaderboard = dictt['leaderboard']
    base_text = texts['usage']
    text = ''
    for i in range(15):
        pkmn = leaderboard[i]
        text += base_text.format(
            pkmn['rank'],
            pkmn['pokemon'],
            pkmn['usage'],
        )
    markup = dictt['markup']

    func.bot_action(app, message, text, markup)


# ===== FAQ command =====
@app.on_message(Filters.command(['faq', 'faq@officerjennyprobot']))
def faq(app, message):
    text = texts['faq']
    app.send_message(
        chat_id=message.chat.id,
        text=text, 
        parse_mode='HTML',
        disable_web_page_preview=True
    )



# ===== About command =====
@app.on_message(Filters.command(['about', 'about@officerjennyprobot']))
def about(app, message):
    text = texts['about']
    markup = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            text='Github',
            url='https://github.com/madboy482/rotom-2.0'
        )
    ]])

    app.send_message(
        chat_id=message.chat.id,
        text=text, 
        reply_markup=markup,
        disable_web_page_preview=True
    )


# ===== Presentation =====
@app.on_message(Filters.create(lambda _, message: message.new_chat_members))
def bot_added(app, message):
    for new_member in message.new_chat_members:
        if new_member.id == 1269349088:
            text = texts['added']
            app.send_message(
                chat_id=message.chat.id,
                text=text
            )
            
@app.on_message(Filters.command(['generation', 'generation@officerjennyprobot']))
async def photo(client: app, message):
   await client.send_message(
      chat_id=message.chat.id,
      text="SELECT FROM THE GENERATION U WANT TO SEE",
      reply_markup=InlineKeyboardMarkup(
           [
                    [
                        InlineKeyboardButton(text="GEN1", callback_data="gen1"),
                        InlineKeyboardButton(text="GEN2", callback_data="gen2"),
                        InlineKeyboardButton(text="GEN3", callback_data="gen3")
                    ],
                    [
                        InlineKeyboardButton(text="GEN4", callback_data="gen4"),
                        InlineKeyboardButton(text="GEN5", callback_data="gen5"),
                        InlineKeyboardButton(text="GEN6", callback_data="gen6")
                    ],
                    [
                        InlineKeyboardButton(text="GEN7", callback_data="gen7"),
                    ]
                ]
            ),
            reply_to_message_id=message.reply_to_message_id,
        )

@app.on_callback_query()
async def cb_handler(client: app, query: CallbackQuery):
        if query.data == "gen1":
            await query.message.edit_text(
                "HERE ARE THE LIST OF GENERATION 1 POKEMONS\n\n`🌟Bulbasaur |🌟Ivysaur`*\n`🌟Venusaur  |🌟Charmander`*\n`🌟Charmeleon|🌟Charizard`\n`🌟Squirtle  |🌟Wartortle`\n`🌟Blastoise |🌟Caterpie`\n`🌟Metapod   |🌟Butterfree`\n`🌟Weedle    |🌟Kakuna`\n`🌟Beedrill  |🌟Pidgey`\n`🌟Pidgeotto |🌟Pidgeot`\n`🌟Rattata   |🌟Raticate`\n`🌟Spearow   |🌟Fearow`\n`🌟Ekans     |🌟Arbok `\n`🌟Pikachu   |🌟Raichu`\n`🌟Sandshrew |🌟Sandslash`\n`🌟Nidoran♀  |🌟Nidorina`\n`🌟Nidoqueen |🌟Nidoran♂`\n`🌟Nidorino  |🌟Nidoking`\n`🌟Clefairy  |🌟Clefable`\n`🌟Vulpix    |🌟Ninetales`\n`🌟Jigglypuff|🌟Wigglytuff `\n`🌟Zubat     |🌟Golbat`\n`🌟Oddish    |🌟Gloom`\n`🌟Vileplume |🌟Paras`\n`🌟Parasect  |🌟Venonat`\n`🌟Venomoth  |🌟Diglett`\n`🌟Dugtrio   |🌟Meowth`\n`🌟Persian   |🌟Psyduck`\n`🌟Golduck   |🌟Mankey`\n`🌟Primeape  |🌟Growlithe`\n`🌟Arcanine  |🌟Poliwag`\n`🌟Poliwhirl |🌟Poliwrath`\n`🌟Abra      |🌟Kadabra`\n`🌟Alakazam  |🌟Machop`\n`🌟Machamp   |🌟Machoke`\n`🌟Farfetch'd|🌟Bellsprout`\n`🌟Weepinbell|🌟Victreebel`\n`🌟Tentacool |🌟Tentacruel`\n`🌟Geodude   |🌟Graveler`\n`🌟Golem     |🌟Ponyta`\n`🌟Rapidash  |🌟Slowpoke`\n`🌟Slowbro   |🌟Magnemite`\n`🌟Magneton  |🌟Doduo`\n`🌟Dodrio    |🌟Seel`\n`🌟Dewgong   |🌟Grimer`\n`🌟Muk       |🌟Shellder`\n`🌟Cloyster  |🌟Gastly`\n`🌟Haunter   |🌟Gengar`\n`🌟Onix      |🌟Drowzee`\n`🌟Hypno     |🌟Krabby`\n`🌟Kingler   |🌟Voltorb`\n`🌟Electrode |🌟Exeggcute`\n`🌟Exeggutor |🌟Cubone`\n`🌟Marowak   |🌟Hitmonlee`\n`🌟Hitmonchan|🌟Lickitung`\n`🌟Koffing   |🌟Weezing`\n`🌟Rhyhorn   |🌟Rhydon`\n`🌟Chansey   |🌟Tangela`\n`🌟Kangaskhan|🌟Horsea`\n`🌟Seadra    |🌟Goldeen`\n`🌟Seaking   |🌟Staryu`\n`🌟Starmie   |🌟Mr.Mime`\n`🌟Scyther   |🌟Jynx`\n`🌟Electabuzz|🌟Magmar`\n`🌟Pinsir    |🌟Tauros`\n`🌟Magikarp  |🌟Gyarados`\n`🌟Lapras    |🌟Ditto`\n`🌟Eevee     |🌟Vaporeon`\n`🌟Jolteon   |🌟Flareon`\n`🌟Porygon   |🌟Omanyte`\n`🌟Omastar   |🌟Kabuto`\n`🌟Kabutops  |🌟Aerodactyl`\n`🌟Snorlax   |🌟Articuno`\n`🌟Zapdos    |🌟Moltres`\n`🌟Dratini   |🌟Dragonair`\n`🌟Dragonite |🌟Mewtwo`\n`🌟Mewㅤㅤㅤㅤ",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="GEN2", callback_data="gen2"
                            ),
                            InlineKeyboardButton(
                                text="GEN3", callback_data="gen3"
                            ),
                            InlineKeyboardButton(
                                text="GEN4", callback_data="gen4"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text="GEN5", callback_data="gen5"
                            ),
                            InlineKeyboardButton(
                                text="GEN6", callback_data="gen6"
                            ),
                            InlineKeyboardButton(
                                text="GEN7", callback_data="gen7"
                            )
                        ]
                    ]
                ),
            )
        elif query.data == "gen2":
            await query.message.edit(
                "HERE ARE THE LIST OF GENERATION 2 POKEMONS\n\n🌟 Chikorita\n🌟 Bayleef\n🌟 Meganium\n🌟 Cyndaquil\n🌟 Quilava\n🌟 Typhlosion\n🌟 Totodile\n🌟 Croconaw\n🌟 Feraligatr\n🌟 Sentret\n🌟 Furret\n🌟 Hoothoot\n🌟 Noctowl\n🌟 Ledyba\n🌟 Ledian\n🌟 Spinarak\n🌟 Ariados\n🌟 Crobat\n🌟 Chinchou\n🌟 Lanturn\n🌟 Pichu\n🌟 Cleffa\n🌟 Igglybuff\n🌟 Togepi\n🌟 Togetic\n🌟 Natu\n🌟 Xatu\n🌟 Mareep\n🌟 Flaaffy\n🌟 Ampharos\n🌟 Bellossom\n🌟 Marill\n🌟 Azumarill\n🌟 Sudowoodo\n🌟 Politoed\n🌟 Hoppip\n🌟 Skiploom\n🌟 Jumpluff\n🌟 Aipom\n🌟 Sunkern\n🌟 Sunflora\n🌟 Yanma\n🌟 Wooper\n🌟 Quagsire\n🌟 Espeon\n🌟 Umbreon\n🌟 Murkrow\n🌟 Slowking\n🌟 Misdreavus\n🌟 Unown\n🌟 Wobbuffet\n🌟 Girafarig\n🌟 Pineco\n🌟 Forretress\n🌟 Dunsparce\n🌟 Gligar\n🌟 Steelix\n🌟 Snubbull\n🌟 Granbull\n🌟 Qwilfish\n🌟 Scizor\n🌟 Shuckle\n🌟 Heracross\n🌟 Sneasel\n🌟 Teddiursa\n🌟 Ursaring\n🌟 Slugma\n🌟 Magcargo\n🌟 Swinub\n🌟 Piloswine\n🌟 Corsola\n🌟 Remoraid\n🌟 Octillery\n🌟 Delibird\n🌟 Mantine\n🌟 Skarmory\n🌟 Houndour\n🌟 Houndoom\n🌟 Kingdra\n🌟 Phanpy\n🌟 Donphan\n🌟 Porygon2\n🌟 Stantler\n🌟 Smeargle\n🌟 Tyrogue\n🌟 Hitmontop\n🌟 Smoochum\n🌟 Elekid\n🌟 Magby\n🌟 Miltank\n🌟 Blissey\n🌟 Raikou\n🌟 Entei\n🌟 Suicune\n🌟 Larvitar\n🌟 Pupitar\n🌟 Tyranitar\n🌟 Lugia\n🌟 Ho-Oh\n🌟 Celebi",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text="GEN1", callback_data="gen1"),
                            InlineKeyboardButton(
                                text="GEN3", callback_data="gen3"
                            ),
                            InlineKeyboardButton(
                                text="GEN4", callback_data="gen4"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text="GEN5", callback_data="gen5"
                            ),
                            InlineKeyboardButton(
                                text="GEN6", callback_data="gen6"
                            ),
                            InlineKeyboardButton(
                                text="GEN7", callback_data="gen7"
                            )
                        ]
                    ]
                ),
            )
        elif query.data == "gen3":
            await query.message.edit(
                "HERE ARE THE LIST OF GENERATION 3 POKEMONS\n\n🌟 Treecko\n🌟 Grovyle\n🌟 Sceptile\n🌟 Torchic\n🌟 Combusken\n🌟 Blaziken\n🌟 Mudkip\n🌟 Marshtomp\n🌟 Swampert\n🌟 Poochyena\n🌟 Mightyena\n🌟 Zigzagoon\n🌟 Linoone\n🌟 Wurmple\n🌟 Silcoon\n🌟 Beautifly\n🌟 Cascoon\n🌟 Dustox\n🌟 Lotad\n🌟 Lombre\n🌟 Ludicolo\n🌟 Seedot\n🌟 Nuzleaf\n🌟 Shiftry\n🌟 Taillow\n🌟 Swellow\n🌟 Wingull\n🌟 Pelipper\n🌟 Ralts\n🌟 Kirlia\n🌟 Gardevoir\n🌟 Surskit\n🌟 Masquerain\n🌟 Shroomish\n🌟 Breloom\n🌟 Slakoth\n🌟 Vigoroth\n🌟 Slaking\n🌟 Nincada\n🌟 Ninjask\n🌟 Shedinja\n🌟 Whismur\n🌟 Loudred\n🌟 Exploud\n🌟 Makuhita\n🌟 Hariyama\n🌟 Azurill\n🌟 Nosepass\n🌟 Skitty\n🌟 Delcatty\n🌟 Sableye\n🌟 Mawile\n🌟 Aron\n🌟 Lairon\n🌟 Aggron\n🌟 Meditite\n🌟 Medicham\n🌟 Electrike\n🌟 Manectric\n🌟 Plusle\n🌟 Minun\n🌟 Volbeat\n🌟 Illumise\n🌟 Roselia\n🌟 Gulpin\n🌟 Swalot\n🌟 Carvanha\n🌟 Sharpedo\n🌟 Wailmer\n🌟 Wailord\n🌟 Numel\n🌟 Camerupt\n🌟 Torkoal\n🌟 Spoink\n🌟 Grumpig\n🌟 Spinda\n🌟 Trapinch\n🌟 Vibrava\n🌟 Flygon\n🌟 Cacnea\n🌟 Cacturne\n🌟 Swablu\n🌟 Altaria\n🌟 Zangoose\n🌟 Seviper\n🌟 Lunatone\n🌟 Solrock\n🌟 Barboach\n🌟 Whiscash\n🌟 Corphish\n🌟 Crawdaught\n🌟 Baltoy\n🌟 Claydol\n🌟 Lileep\n🌟 Cradily\n🌟 Anorith\n🌟 Armaldo\n🌟 Feebas\n🌟 Milotic\n🌟 Castform\n🌟 Kecleon\n🌟 Shuppet\n🌟 Banette\n🌟 Duskull\n🌟 Dusclops\n🌟 Tropius\n🌟 Chimecho\n🌟 Absol\n🌟 Wynaut\n🌟 Snorunt\n🌟 Glalie\n🌟 Spheal\n🌟 Sealeo\n🌟 Walrein\n🌟 Clamperl\n🌟 Huntail\n🌟 Gorebyss\n🌟 Relicanth\n🌟 Luvdisc\n🌟 Bagon\n🌟 Shelgon\n🌟 Salamence\n🌟 Beldum\n🌟 Metang\n🌟 Metagross\n🌟 Regirock\n🌟 Regice\n🌟 Registeel\n🌟 Latias\n🌟 Latios\n🌟 Kyogre\n🌟 Groudon\n🌟 Rayquaza\n🌟 Jirachu\n🌟 Deoxys ",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text="GEN1", callback_data="gen1"),
                            InlineKeyboardButton(
                                text="GEN2", callback_data="gen2"
                            ),
                            InlineKeyboardButton(
                                text="GEN4", callback_data="gen4"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text="GEN5", callback_data="gen5"
                            ),
                            InlineKeyboardButton(
                                text="GEN6", callback_data="gen6"
                            ),
                            InlineKeyboardButton(
                                text="GEN7", callback_data="gen7"
                            )
                        ]
                    ]
                ),
            )
        elif query.data == "gen4":
            await query.message.edit(
                "HERE ARE THE LIST OF GENERATION 4 POKEMONS\n\n🌟 Turtwig\n🌟 Grotle\n🌟 Torterra\n🌟 Chimchar\n🌟 Monferno\n🌟 Infernape\n🌟 Piplup\n🌟 Prinplup\n🌟 Empoleon\n🌟 Starly\n🌟 Staravia\n🌟 Staraptor\n🌟 Bidoof\n🌟 Bibarel\n🌟 Kricketot\n🌟 Kricketune\n🌟 Shinx\n🌟 Luxio\n🌟 Luxray\n🌟 Budew\n🌟 Roserade\n🌟 Cranidos\n🌟 Rampardos\n🌟 Shieldon\n🌟 Bastiodon\n🌟 Burmy\n🌟 Wormadam\n🌟 Mothim\n🌟 Combee\n🌟 Vespiquen\n🌟 Pachirisu\n🌟 Buizel\n🌟 Floatzel\n🌟 Cherubi\n🌟 Cherrim\n🌟 Shellos\n🌟 Gastrodon\n🌟 Ambipom\n🌟 Drifloon\n🌟 Drifblim\n🌟 Buneary\n🌟 Lopunny\n🌟 Mismagius\n🌟 Honchkrow\n🌟 Glameow\n🌟 Purugly\n🌟 Chingling\n🌟 Stunky\n🌟 Skuntank\n🌟 Bronzor\n🌟 Bronzong\n🌟 Bonsly\n🌟 MimeJr.\n🌟 Happiny\n🌟 Chatot\n🌟 Spiritomb\n🌟 Gible\n🌟 Gabite\n🌟 Garchomp\n🌟 Munchlax\n🌟 Riolu\n🌟 Lucario\n🌟 Hippopotas\n🌟 Hippowdon\n🌟 Skorupi\n🌟 Drapion\n🌟 Croagunk\n🌟 Toxicroak\n🌟 Carnivine\n🌟 Finneon\n🌟 Lumineon\n🌟 Mantyke\n🌟 Snover\n🌟 Abomasnow\n🌟 Weavile\n🌟 Magnezone\n🌟 Lickilicky\n🌟 Rhyperior\n🌟 Tangrowth\n🌟 Electivire\n🌟 Magmortar\n🌟 Togekiss\n🌟 Yanmega\n🌟 Leafeon\n🌟 Glaceon\n🌟 Gliscor\n🌟 Mamoswine\n🌟 Porygon-Z\n🌟 Gallade\n🌟 Probopass\n🌟 Dusknoir\n🌟 Froslass\n🌟 Rotom\n🌟 Uxie\n🌟 Mesprit\n🌟 Azelf\n🌟 Dialga\n🌟 Palkia\n🌟 Heatran\n🌟 Regigigas\n🌟 Giratina\n🌟 Cresselia\n🌟 Phione\n🌟 Manaphy\n🌟 Darkrai\n🌟 Shaymin\n🌟 Arceus",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text="GEN1", callback_data="gen1"),
                            InlineKeyboardButton(
                                text="GEN2", callback_data="gen2"
                            ),
                            InlineKeyboardButton(
                                text="GEN3", callback_data="gen3"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text="GEN5", callback_data="gen5"
                            ),
                            InlineKeyboardButton(
                                text="GEN6", callback_data="gen6"
                            ),
                            InlineKeyboardButton(
                                text="GEN7", callback_data="gen7"
                            )
                        ]
                    ]
                ),
            )
        elif query.data == "gen5":
            await query.message.edit(
                "HERE ARE THE LIST OF GENERATION 5 POKEMONS\n\n🌟Victini\n🌟 Snivy\n🌟 Servine\n🌟 Serperior\n🌟 Tepig\n🌟 Pignite\n🌟 Emboar\n🌟 Oshawott\n🌟 Dewott\n🌟 Samurott\n🌟 Patrat\n🌟 Watchog\n🌟 Lillipup\n🌟 Herdier\n🌟 Stoutland\n🌟 Purrloin\n🌟 Liepard\n🌟 Pansage\n🌟 Simisage\n🌟 Pansear\n🌟 Simisear\n🌟 Panpour\n🌟 Simipour\n🌟 Munna\n🌟 Musharna\n🌟 Pidove\n🌟 Tranquill\n🌟 Unfezant\n🌟 Blitzle\n🌟 Zebstrika\n🌟 Roggenrola\n🌟 Boldore\n🌟 Gigalith\n🌟 Woobat\n🌟 Swoobat\n🌟 Drilbur\n🌟 Excadrill\n🌟 Audino\n🌟 Timburr\n🌟 Gurdurr\n🌟 Conkeldurr\n🌟 Tympole\n🌟 Palpitoad\n🌟 Seismitoad\n🌟 Throh\n🌟 Sawk\n🌟 Sewaddle\n🌟 Swadloon\n🌟 Leavanny\n🌟 Venipede\n🌟 Whirlipede\n🌟 Scolipede\n🌟 Cottonee\n🌟 Whimsicott\n🌟 Petilil\n🌟 Lilligant\n🌟 Basculin\n🌟 Sandile\n🌟 Krokorok\n🌟 Krookodile\n🌟 Darumaka\n🌟 Darmanitan\n🌟 Maractus\n🌟 Dwebble\n🌟 Crustle\n🌟 Scraggy\n🌟 Scrafty\n🌟 Sigilyph\n🌟 Yamask\n🌟 Cofagrigus\n🌟 Tirtouga\n🌟 Carracosta\n🌟 Archen\n🌟 Archeops\n🌟 Trubbish\n🌟 Garbodor\n🌟 Zorua\n🌟 Zoroark\n🌟 Minccino\n🌟 Cinccino\n🌟 Gothita\n🌟 Gothorita\n🌟 Gothitelle\n🌟 Solosis\n🌟 Duosion\n🌟 Reuniclus\n🌟 Ducklett\n🌟 Swanna\n🌟 Vanillite\n🌟 Vanillish\n🌟 Vanilluxe\n🌟 Deerling\n🌟 Sawsbuck\n🌟 Emolga\n🌟 Karrablast\n🌟 Escavalier\n🌟 Foongus\n🌟 Amoonguss\n🌟 Frillish\n🌟 Jellicent\n🌟 Alomomola\n🌟 Joltik\n🌟 Galvantula\n🌟 Ferroseed\n🌟 Ferrothorn\n🌟 Klink\n🌟 Klang\n🌟 Klinklang\n🌟 Tynamo\n🌟 Eelektrik\n🌟 Eelektross\n🌟 Elgyem\n🌟 Beheeyem\n🌟 Litwick\n🌟 Lampent\n🌟 Chandelure\n🌟 Axew\n🌟 Fraxure\n🌟 Haxorus\n🌟 Cubchoo\n🌟 Beartic\n🌟 Cryogonal\n🌟 Shelmet\n🌟 Accelgor\n🌟 Stunfisk\n🌟 Mienfoo\n🌟 Mienshao\n🌟 Druddigon\n🌟 Golett\n🌟 Golurk\n🌟 Pawniard\n🌟 Bisharp\n🌟 Bouffalant\n🌟 Rufflet\n🌟 Braviary\n🌟 Vullaby\n🌟 Mandibuzz\n🌟 Heatmor\n🌟 Durant\n🌟 Deino\n🌟 Zweilous\n🌟 Hydreigon\n🌟 Larvesta\n🌟 Volcarona\n🌟 Cobalion\n🌟 Terrakion\n🌟 Virizion\n🌟 Tornadus\n🌟 Thundurus\n🌟 Reshiram\n🌟 Zekrom\n🌟 Landorus\n🌟 Kyurem\n🌟 Keldeo\n🌟 Meloetta\n🌟 Genesect",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text="GEN1", callback_data="gen1"),
                            InlineKeyboardButton(
                                text="GEN2", callback_data="gen2"
                            ),
                            InlineKeyboardButton(
                                text="GEN3", callback_data="gen3"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text="GEN4", callback_data="gen4"
                            ),
                            InlineKeyboardButton(
                                text="GEN6", callback_data="gen6"
                            ),
                            InlineKeyboardButton(
                                text="GEN7", callback_data="gen7"
                            )
                        ]
                    ]
                ),
            )
        elif query.data == "gen6":
            await query.message.edit(
                "**HERE ARE THE LIST OF GENERATION 6 POKEMONS\n\n🌟Chespin\n🌟 Quilladin\n🌟 Chesnaught\n🌟 Fennekin\n🌟 Braixen\n🌟 Delphox\n🌟 Froakie\n🌟 Frogadier\n🌟 Greninja\n🌟 Bunnelby\n🌟 Diggersby\n🌟 Fletchling\n🌟 Fletchinder\n🌟 Talonflame\n🌟 Scatterbug\n🌟 Spewpa\n🌟 Vivillon\n🌟 Litleo\n🌟 Pyroar\n🌟 Flabébé\n🌟 Floette\n🌟 Florges\n🌟 Skiddo\n🌟 Gogoat\n🌟 Pancham\n🌟 Pangoro\n🌟 Furfrou\n🌟 Espurr\n🌟 Meowstic\n🌟 Honedge\n🌟 Doublade\n🌟 Aegislash\n🌟 Spritzee\n🌟 Aromatisse\n🌟 Swirlix\n🌟 Slurpuff\n🌟 Inkay\n🌟 Malamar\n🌟 Binacle\n🌟 Barbaracle\n🌟 Skrelp\n🌟 Dragalge\n🌟 Clauncher\n🌟 Clawitzer\n🌟 Helioptile\n🌟 Heliolisk\n🌟 Tyrunt\n🌟 Tyrantrum\n🌟 Amaura\n🌟 Aurorus\n🌟 Sylveon\n🌟 Hawlucha\n🌟 Dedenne\n🌟 Carbink\n🌟 Goomy\n🌟 Sliggoo\n🌟 Goodra\n🌟 Klefki\n🌟 Phantump\n🌟 Trevenant\n🌟 Pumpkaboo\n🌟 Gourgeist\n🌟 Bergmite\n🌟 Avalugg\n🌟 Noibat\n🌟 Noivern\n🌟 Xerneas\n🌟 Yveltal\n🌟 Zygarde\n🌟 Diancie\n🌟 Hoopa\n🌟 Volcanion",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text="GEN1", callback_data="gen1"),
                            InlineKeyboardButton(
                                text="GEN2", callback_data="gen2"
                            ),
                            InlineKeyboardButton(
                                text="GEN3", callback_data="gen3"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text="GEN4", callback_data="gen4"
                            ),
                            InlineKeyboardButton(
                                text="GEN5", callback_data="gen5"
                            ),
                            InlineKeyboardButton(
                                text="GEN7", callback_data="gen7"
                            )
                        ]
                    ]
                ),
            )
        elif query.data == "gen7":
            await query.message.edit(
                "HERE ARE THE LIST OF GENERATION 7 POKEMONS\n\n🌟 Alolan Rattata\n🌟 Alolan Raticate\n🌟 Alolan Raichu\n🌟 Alolan Sandshrew\n🌟 Alolan Sandslash\n🌟 Alolan Vulpix\n🌟 Alolan Ninetales\n🌟 Alolan Diglett\n🌟 Alolan Dugtrio\n🌟 Alolan Meowth\n🌟 Alolan Persian\n🌟 Alolan Geodude\n🌟 Alolan Graveler\n🌟 Alolan Golem\n🌟 Alolan Grimer\n🌟 Alolan Muk\n🌟 Alolan Exeggutor\n🌟 Alolan Marowak\n🌟 Rowlet\n🌟 Dartrix\n🌟 Decidueye\n🌟 Litten\n🌟 Torracat\n🌟 Incineroar\n🌟 Popplio\n🌟 Brionne\n🌟 Primarina\n🌟 Pikipek\n🌟 Trumbeak\n🌟 Toucannon\n🌟 Yungoos\n🌟 Gumshoos\n🌟 Grubbin\n🌟 Charjabug\n🌟 Vikavolt\n🌟 Crabrawler\n🌟 Crabominable\n🌟 Oricorio\n🌟 Cutiefly\n🌟 Ribombee\n🌟 Rockruff\n🌟 Lycanroc\n🌟 Wishiwashi\n🌟 Mareanie\n🌟 Toxapex\n🌟 Mudbray\n🌟 Mudsdale\n🌟 Dewpider\n🌟 Araquanid\n🌟 Fomantis\n🌟 Lurantis\n🌟 Morelull\n🌟 Shiinotic\n🌟 Salandit\n🌟 Salazzle\n🌟 Stufful\n🌟 Bewear\n🌟 Bounsweet\n🌟 Steenee\n🌟 Tsareena\n🌟 Comfey\n🌟 Oranguru\n🌟 Passimian\n🌟 Wimpod\n🌟 Golisopod\n🌟 Sandygast\n🌟 Palossand\n🌟 Pyukumuku\n🌟 Type:Null\n🌟 Silvally\n🌟 Minior\n🌟 Komala\n🌟 Turtonator\n🌟 Togedemaru\n🌟 Mimikyu\n🌟 Bruxish\n🌟 Drampa\n🌟 Dhelmise\n🌟 Jangmo-o\n🌟 Hakamo-o\n🌟 Kommo-o\n🌟 Tapu-Koko\n🌟 Tapu-Lele\n🌟 Tapu-Bulu\n🌟 Tapu-Fini\n🌟 Cosmog\n🌟 Cosmoem\n🌟 Solgaleo\n🌟 Lunala\n🌟 Nihilego\n🌟 Buzzwole\n🌟 Pheromosa\n🌟 Xurkitree\n🌟 Celesteela\n🌟 Kartana\n🌟 Guzzlord\n🌟 Necrozma\n🌟 Magearna\n🌟 Marshadow\n🌟 Poipole\n🌟 Naganadel\n🌟 Stakataka\n🌟 Blacephalon\n🌟 Zeraora\n🌟 Meltan\n🌟 Melmetal",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text="GEN1", callback_data="gen1"),
                            InlineKeyboardButton(
                                text="GEN2", callback_data="gen2"
                            ),
                            InlineKeyboardButton(
                                text="GEN3", callback_data="gen3"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text="GEN4", callback_data="gen4"
                            ),
                            InlineKeyboardButton(
                                text="GEN5", callback_data="gen5"
                            ),
                            InlineKeyboardButton(
                                text="GEN6", callback_data="gen6"
                            )
                        ]
                    ]
                ),
            )



app.run()
