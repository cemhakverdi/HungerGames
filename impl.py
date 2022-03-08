import sqlite3
import PySimpleGUI as sg
from enum import Enum


class User(Enum):
    Mentor = 1
    GameMaker = 2
    Sponsor = 3


con = sqlite3.connect('impl_original.db')
cur = con.cursor()

# Constants
ACTION_LOGIN = "Login"
ACTION_LOGOUT = "Logout"


def create_login_window():
    layout_login = [[sg.Text('SSN:', size=(10, 1)), sg.Input(size=(20, 1), key='ssn')],
                    [sg.Text('Password:', size=(10, 1)), sg.Input(size=(20, 1), key='password', password_char="*")],
                    [sg.Button(ACTION_LOGIN, bind_return_key=True)]]

    return sg.Window("Login Window", element_justification="right", layout=layout_login, resizable=True)


def create_dashboard_window():
    if user_type == User.GameMaker:
        cur.execute("Select Year_id, Description, Setting_Type from Game "
                    "INNER JOIN GameMaker on Game.SSN = GameMaker.SSN where GameMaker.SSN = ?", (user_id,))
        row = cur.fetchall()

        data = [f"{item[0]}, {item[1]}, {item[2]}" for item in row]

        user_layout = [
            [sg.Text("All Games:")],
            [sg.Listbox(values=data, size=(40, 5), key="GameMakerListOnClick", enable_events=True)],
            [sg.Button("Mentors", key="GameMakerSeeAllMentors"),
             sg.Button("Interactions", key="GameMakerCreateInteraction")]
        ]
    elif user_type == User.Sponsor:
        cur.execute("SELECT Tribute.Tribute_id, Tribute.Name, Tribute.Surname FROM Tribute")
        row = cur.fetchall()
        data = [f"{item[0]}, {item[1]}, {item[2]}" for item in row]

        user_layout = [
            [sg.Text('Game:', size=(10, 1)), sg.Input(size=(15, 1), key='game')],
            [sg.Text('Name:', size=(10, 1)), sg.Input(size=(15, 1), key='name')],
            [sg.Text('Status:', size=(10, 1)), sg.Input(size=(15, 1), key='status')],
            [sg.Text('District:', size=(10, 1)), sg.Input(size=(15, 1), key='district')],
            [sg.Listbox(values=data, size=(40, 5), key="SponsorSeeTribute", enable_events=True)],
            [sg.Button("Filter", key="SponsorFilterTributes")],
            [sg.Button("Credit Card", key="SponsorShowCreditCard")]
        ]
    elif user_type == User.Mentor:
        cur.execute("Select Tribute.Tribute_id, Tribute.Name, Tribute.Surname "
                    "from Tribute INNER JOIN Mentor on Tribute.SSN = Mentor.SSN "
                    "where Mentor.SSN = ?", (user_id,))
        row = cur.fetchall()

        data = [f"{item[0]}, {item[1]}, {item[2]}" for item in row]

        user_layout = [
            [sg.Text("List Of Tributes:")],
            [sg.Listbox(values=data, size=(40, 5), key="MentorTributeListOnClick", enable_events=True)],
        ]
    else:
        raise Exception("Illegal type exception")

    return sg.Window(f"{user_type.name} Dashboard", user_layout)


def create_game_maker_add_rule_window():
    global year_id

    add_rule_layout = [
        [sg.Text('Rule Id:', size=(10, 1)), sg.Input(size=(10, 1), key='rule_id')],
        [sg.Text('Content:', size=(10, 1)), sg.Input(size=(10, 1), key='content')],
        [sg.Button("Add Rule", key="GameMakerAddRule")]
    ]

    return sg.Window(f"Rules for Game: {year_id}", add_rule_layout)


def create_game_maker_list_all_rules_window(year):
    global year_id
    year_id = year

    cur.execute("select AdditionalRule.Rule_id, AdditionalRule.Year_id, AdditionalRule.Content "
                "from AdditionalRule  inner join Game on Game.Year_id = AdditionalRule.Year_id where Game.Year_id = ?",
                (year_id,))
    row = cur.fetchall()

    data = [f"{item[0]}, {item[1]}, {item[2]}" for item in row]

    list_all_rules_layout = [
        [sg.Text(f"All Rules of Game {year}")],
        [sg.Listbox(values=data, size=(40, 10), key="GameMakerAllRulesListOnClick")],
        [sg.Button("Add Rule", key="GameMakerListRulesAddRule")]
    ]

    return sg.Window(f"Rules for Game: {year_id}", list_all_rules_layout)


def create_game_maker_send_award_window(def_mentor_ssn):
    global mentor_ssn

    mentor_ssn = def_mentor_ssn

    award_layout = [
        [sg.Text('Award Name:', size=(10, 1)), sg.Input(size=(10, 1), key='award_name')],
        [sg.Button("Send Award", key="GameMakerSendAward")]
    ]

    return sg.Window(f"Send Award", award_layout)


def create_game_maker_add_interaction_window():
    interaction_layout = [
        [sg.Text('Interaction Id:', size=(10, 1)), sg.Input(size=(15, 1), key='interaction_id')],
        [sg.Text('Interactee Id:', size=(10, 1)), sg.Input(size=(15, 1), key='interactee_id')],
        [sg.Text('Interacted Id:', size=(10, 1)), sg.Input(size=(15, 1), key='interacted_id')],
        [sg.Text('Date:', size=(10, 1)), sg.Input('', size=(15, 1), key="date", disabled=True),
         sg.CalendarButton('Choose Date', size=(10, 1), target=(3, 1), format="%d/%m/%Y")],
        [sg.Text('Description:', size=(10, 1)), sg.Input(size=(25, 1), key='description')],
        [sg.Button("Add Interaction", key="GameMakerAddInteraction")]
    ]

    return sg.Window(f"Add Interaction", interaction_layout)


def create_game_maker_list_mentors_window():
    cur.execute("Select Mentor.SSN, User.Name from Mentor inner join User on Mentor.SSN = User.SSN")
    row = cur.fetchall()

    data = [f"{item[0]}, {item[1]}" for item in row]

    mentors_layout = [
        [sg.Text("Click To Send Award:")],
        [sg.Listbox(values=data, size=(40, 10), key="GameMakerMentorListOnClick", enable_events=True)]
    ]

    return sg.Window(f"Mentors", mentors_layout)


def create_mentor_list_all_tributes_window(def_tribute_id):
    global tribute_id
    tribute_id = def_tribute_id

    cur.execute("Select Tribute.Status, Interaction.Description, Interaction_date "
                "from Interaction "
                "INNER JOIN Tribute on Tribute.Tribute_id = Interaction.Interactee_id or Tribute.Tribute_id = Interaction.Interacted_id "
                "where Tribute_id = ? order by Interaction_date", (tribute_id,))
    row = cur.fetchall()
    data = [f"{item[0]}, {item[1]}, {item[2]}" for item in row]

    list_all_rules_layout = [
        [sg.Listbox(values=data, size=(40, 10))],
        [sg.Button("Pending Gifts", key="MentorSeeAllGifts")]
    ]

    return sg.Window(f"Properties of Tribute {tribute_id}", list_all_rules_layout)


def create_mentor_list_all_gifts_window():
    cur.execute("SELECT GivesGift.Gift_name from GivesGift where GivesGift.Tribute_id = ?", (tribute_id,))
    row = cur.fetchall()
    data = [f"{item[0]}" for item in row]

    list_all_rules_layout = [
        [sg.Text("Click To Authorize:")],
        [sg.Listbox(values=data, size=(40, 10), key="MentorAddGift", enable_events=True)],
    ]

    return sg.Window(f"Gifts of Tribute {tribute_id}", list_all_rules_layout)


def create_mentor_add_gift_window(def_gif_name):
    global gift_name
    gift_name = def_gif_name

    list_all_rules_layout = [
        [sg.Text('Gift Amount:', size=(10, 1)), sg.Input(size=(15, 1), key='amount')],
        [sg.Text('Date:', size=(10, 1)), sg.Input('', size=(15, 1), key="date", disabled=True),
         sg.CalendarButton('Choose Date', size=(10, 1), target=(1, 1), format="%d/%m/%Y")],
        [sg.Button("Authorize Gift", key="MentorAuthorizeGift")]
    ]

    return sg.Window(f"Authorize Gifts for Tribute {tribute_id}", list_all_rules_layout)


def create_sponsor_filter_tributes_window(game, name, status, district):
    query = "SELECT Tribute.Tribute_id, Tribute.Name, Tribute.Surname " \
            "from Tribute LEFT join Game on Tribute.Year_id = Game.Year_id " \
            "WHERE Tribute.Name LIKE '%%' "

    dataset = []

    if name != "":
        query += "AND Tribute.name LIKE ? "
        dataset.append(f"%{name}%")
    if status != "":
        query += "AND Tribute.Status LIKE ? "
        dataset.append(f"%{status}%")
    if district != "":
        query += "AND Tribute.District_no = ? "
        dataset.append(int(district))
    if game != "":
        query += "AND Tribute.Year_id = ? "
        dataset.append(int(game))

    cur.execute(query, (tuple(i for i in dataset)))
    row = cur.fetchall()
    data = [f"{item[0]}, {item[1]}, {item[2]}" for item in row]

    user_layout = [
        [sg.Text('Game:', size=(10, 1)), sg.Input(size=(15, 1), key='game')],
        [sg.Text('Name:', size=(10, 1)), sg.Input(size=(15, 1), key='name')],
        [sg.Text('Status:', size=(10, 1)), sg.Input(size=(15, 1), key='status')],
        [sg.Text('District:', size=(10, 1)), sg.Input(size=(15, 1), key='district')],
        [sg.Listbox(values=data, size=(40, 5), key="SponsorSeeTribute", enable_events=True)],
        [sg.Button("Filter", key="SponsorFilterTributes")],
        [sg.Button("Credit Card", key="SponsorShowCreditCard")]
    ]

    return sg.Window(f"List of Tribute", user_layout)


def create_sponsor_see_tribute_window(def_tribute_id):
    global tribute_id
    tribute_id = def_tribute_id

    cur.execute("SELECT Gift_name, Price, Description FROM gift")
    row = cur.fetchall()
    data = [f"{item[0]}, {item[1]}, {item[2]}" for item in row]

    list_all_rules_layout = [
        [sg.Listbox(values=data, size=(40, 10), key="SponsorSelectGift", enable_events=True)],
    ]

    return sg.Window(f"Select a Gift For This Tribute {tribute_id}", list_all_rules_layout)


def create_sponsor_show_credit_card():
    global user_id

    cur.execute("SELECT Sponsor.Credit_Card FROM Sponsor WHERE Sponsor.SSN = ?", (user_id,))
    row = cur.fetchone()[0]

    list_all_rules_layout = [
        [sg.Text(f'Current Credit Card: {row}', size=(30, 1))],
        [sg.Text('New Credit Card:', size=(15, 1)), sg.Input(size=(20, 1), key='credit_card')],
        [sg.Button("Change Credit Card", key="SponsorChangeCreditCard")]
    ]

    return sg.Window(f"Credit Card of Sponsor {user_id}", list_all_rules_layout)


def action_login():
    global window
    global user_id
    global user_type

    user_id = values['ssn']
    password = values['password']
    if user_id == '':
        sg.popup('Missing user SSN!')
    elif password == '':
        sg.popup('Missing password name!')
    else:
        cur.execute('SELECT Name FROM User WHERE User.SSN = ? AND User.Password = ?', (user_id, password))
        row = cur.fetchone()

        if row is None:
            sg.popup('No such user!')
        else:
            name = row[0]
            sg.popup("Welcome, {}".format(name))

            window.close()

            if len(cur.execute("SELECT SSN from User where SSN in (Select SSN from GameMaker WHERE SSN = ?)",
                               (user_id,)).fetchall()) == 1:
                user_type = User.GameMaker
            elif len(cur.execute("Select SSN from User where SSN in (Select SSN from Sponsor WHERE SSN = ?)",
                                 (user_id,)).fetchall()) == 1:
                user_type = User.Sponsor
            elif len(cur.execute("Select SSN from User where SSN in (Select SSN from Mentor WHERE SSN = ?)",
                                 (user_id,)).fetchall()) == 1:
                user_type = User.Mentor
            else:
                raise Exception("Illegal type exception")
        window = create_dashboard_window()


def action_game_maker_add_rule(rule_id, content):
    global window

    try:
        rule_id = int(rule_id)
        assert rule_id > 0
    except Exception:
        sg.popup("Rule id should be a positive number!")
        return

    cur.execute("Select count(Rule_id) from AdditionalRule where Rule_id = ?", (rule_id,))
    if cur.fetchone()[0] == 1:
        sg.popup("This rule id is already defined!")
    else:
        cur.execute("INSERT INTO AdditionalRule(Rule_id, Year_id, Content) Values(?, ?, ?) ",
                    (rule_id, year_id, content))
        sg.popup("Rule successfully added!")
        window.close()
        window = create_dashboard_window()


def action_game_maker_add_interaction(interaction_id, interactee_id, interacted_id, date, description):
    global window

    try:
        interaction_id = int(interaction_id)
        interactee_id = int(interactee_id)
        interacted_id = int(interacted_id)
        assert str(date) != ""
    except Exception:
        sg.popup("All ids should be positive numbers!")
        return

    result1 = cur.execute("Select count(Interaction_id) from Interaction where Interaction_id = ?", (interaction_id,)).fetchone()[0]
    result2 = cur.execute("Select count(Tribute_id) from Tribute where Tribute.Tribute_id = ?", (interactee_id,)).fetchone()[0]
    result3 = cur.execute("Select count(Tribute_id) from Tribute where Tribute.Tribute_id = ?", (interacted_id,)).fetchone()[0]
    if result1 == 1:
        sg.popup("This interaction id is already defined!")
    elif result2 == 0 or result3 == 0:
        sg.popup("This tribute does not exist!")
    else:
        cur.execute(
            "INSERT INTO Interaction(Interactee_id, Interacted_id, Interaction_id, Interaction_date, Description) "
            "VALUES(?, ?, ?, ?, ?)",
            (interactee_id, interacted_id, interaction_id, date, description))
        sg.popup("Interaction successfully added!")
        window.close()
        window = create_dashboard_window()


def action_game_maker_send_award(def_award_name):
    global window

    cur.execute("SELECT COUNT(Award_name) FROM Awards WHERE Award_name = ?", (def_award_name,))
    if cur.fetchone()[0] == 1:
        sg.popup("This award is already given!")
    else:
        cur.execute("Insert into Awards(Award_name, SSN) VALUES(?, ?)", (def_award_name, mentor_ssn))
        sg.popup("Award successfully given!")
        window.close()
        window = create_dashboard_window()


def action_mentor_authorize_gift(amount, date):
    global window
    global tribute_id
    global gift_name

    try:
        amount = int(amount)
        assert str(date) != ""
    except Exception:
        sg.popup("Gift amount should be a positive number!")
        return

    cur.execute("select GivesGift.SSN from GivesGift where GivesGift.Tribute_id = ?", (tribute_id,))
    ssn = cur.fetchone()[0]

    cur.execute("select SSN, Gift_name, Tribute_id "
                "from Authorizes "
                "where SSN = ? AND Gift_name = ? AND Tribute_id = ? ",
                (ssn, gift_name, tribute_id))
    result = cur.fetchall()

    if result:
        sg.popup("This tribute already has this gift!")
    else:
        cur.execute("INSERT INTO GiftGiven(SSN, amount, auth_date) values(?, ?, ?)", (ssn, amount, date))
        cur.execute("insert into Authorizes(SSN, Gift_name, Tribute_id, Authorization_Date, Mentor_SSN) "
                    "values(?, ?, ?, ?, ?)",
                    (ssn, gift_name, tribute_id, date, user_id))
        sg.popup("Gift successfully authorized!")
        window = create_dashboard_window()

    # window.close()


def action_sponsor_send_gift(gift_name):
    global window
    global tribute_id
    global user_id

    sg.popup(f"Gift successfully sent to {tribute_id}!")

    cur.execute("insert into GivesGift(SSN, Gift_name, Tribute_id) values(?, ?, ?)",
                (user_id, gift_name, tribute_id))

    window.close()
    window = create_dashboard_window()


def action_sponsor_change_credit_card(credit_card):
    global window
    global tribute_id
    global user_id

    try:
        credit_card = int(credit_card)
        assert len(str(credit_card)) == 16
    except Exception:
        sg.popup("Credit card should be number and its length should be 16!")
        return

    sg.popup(f"Credit Card successfully changed!")

    cur.execute("update Sponsor set Credit_Card = ? where Sponsor.SSN = ?",
                (credit_card, user_id,))

    window.close()
    window = create_dashboard_window()


if __name__ == '__main__':
    window = create_login_window()

    while True:
        event, values = window.read()

        # Login
        if event == ACTION_LOGIN:
            action_login()
        if event == ACTION_LOGOUT:
            window.close()
            window = create_login_window()

        # GameMaker Screen
        if event == 'GameMakerListOnClick':
            window.close()
            window = create_game_maker_list_all_rules_window(str(values["GameMakerListOnClick"][0]).split(",")[0])
        if event == 'GameMakerListRulesAddRule':
            window.close()
            window = create_game_maker_add_rule_window()
        if event == 'GameMakerMentorListOnClick':
            window.close()
            window = create_game_maker_send_award_window(str(values["GameMakerMentorListOnClick"][0]).split(",")[0])
        if event == 'GameMakerCreateInteraction':
            window.close()
            window = create_game_maker_add_interaction_window()
        if event == 'GameMakerSeeAllMentors':
            window.close()
            window = create_game_maker_list_mentors_window()
        if event == 'GameMakerAddRule':
            action_game_maker_add_rule(values["rule_id"], values["content"])
        if event == 'GameMakerAddInteraction':
            action_game_maker_add_interaction(values["interaction_id"], values["interactee_id"],
                                              values["interacted_id"], values["date"],
                                              values["description"])
        if event == 'GameMakerSendAward':
            action_game_maker_send_award(values["award_name"])

        # Mentor Screen
        if event == 'MentorTributeListOnClick':
            window.close()
            window = create_mentor_list_all_tributes_window(str(values["MentorTributeListOnClick"][0]).split(",")[0])
        if event == 'MentorSeeAllGifts':
            window.close()
            window = create_mentor_list_all_gifts_window()
        if event == 'MentorAddGift':
            window.close()
            window = create_mentor_add_gift_window(str(values["MentorAddGift"][0]))
        if event == 'MentorAuthorizeGift':
            action_mentor_authorize_gift(values["amount"], values["date"])

        # Sponsor Screen
        if event == 'SponsorSeeTribute':
            window.close()
            window = create_sponsor_see_tribute_window(str(values["SponsorSeeTribute"][0]).split(",")[0])
        if event == 'SponsorFilterTributes':
            window.close()
            window = create_sponsor_filter_tributes_window(
                values["game"], values["name"], values["status"], values["district"]
            )
        if event == 'SponsorSelectGift':
            action_sponsor_send_gift(str(values["SponsorSelectGift"][0]).split(",")[0])
        if event == 'SponsorShowCreditCard':
            window.close()
            window = create_sponsor_show_credit_card()
        if event == 'SponsorChangeCreditCard':
            action_sponsor_change_credit_card(values["credit_card"])

        # General
        if event == sg.WIN_CLOSED:
            print("Close Event")
            break

    window.close()

    con.commit()
    con.close()
