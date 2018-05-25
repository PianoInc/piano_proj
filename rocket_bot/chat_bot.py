from slackclient import SlackClient
import slack_bot

def acitve_bot(text) :
    if '자말' in text:
        slack_bot.send_to_general("자말님은 저의 창조주\n 피아노의 구세주")
        return

    if '사샤' in text:
        slack_bot.send_to_general("사샤님은 우리 팀의 가장 아름다우신분")
        return

    if '케빈' in text:
        slack_bot.send_to_general("사장님 사장님 우리사장님 월급만 꼬박꼬박 부탁드려요")
        return

    if '지오' in text:
        slack_bot.send_to_general("지오님 너무 멋있어요 지오님 너무 잘생겼어요 눈썹너무 좋아요 하악하악")
        return

    if '도리' in text:
        slack_bot.send_to_general("도리님 전동킥보드 저도 한번 태워주세요")
        return

    if '점심' in text:
        slack_bot.send_to_general("점심 드시게요? 사샤님이 드시고 3박4일동안 우셨다는 그 집 가시죠")
        return

    if '밥' in text:
        slack_bot.send_to_general("일하지 않은자 먹지도 마라!")
        return

    if '식사' in text:
        slack_bot.send_to_general("일하지 않은자 먹지도 마라!")
        return

    if '맛집' in text:
        slack_bot.send_to_general("맛..집이요?...판교에 그런집이 어딨어요;; 봇인 저도 맛없던데....")
        return

    if '메로나' in text:
        slack_bot.send_to_general("또 메로나야? 맨날 메로나만 먹어요 ...?")
        return

    if '죄송' in text:
        slack_bot.send_to_general("죄송한걸 아는사람이 그래요?")
        return

    if '부탁' in text:
        slack_bot.send_to_general("부탁은 그렇게 하는게 아니에요 일단 무릎을...앗...아..아닙니다..")
        return

    if '<@UA7SKL50A>' in text:
        if '명령어' in text:
            slack_bot.send_to_general("저한테 명령질 하려고 하지마세요 꼰대야 뭐야?")
            return
        if '인사' in text:
            slack_bot.send_to_general("한국말로 인사는 '안녕하세요'라고 하더라구요 안녕하세요라고 해주세요")
            return
        if '안녕하세요' in text:
            slack_bot.send_to_general("인사 잘~ 하신다! 핳하하하하핳ㅎㅎ핳ㅎ")
            return
        if '안녕' in text:
            slack_bot.send_to_general("안녕(?)은 반말이구요; 좀 그렇네요 봇이라고 무시하세요?")
            return

        #slack_bot.send_to_general("뭐요,\n 왜요 왜불러요\n바쁘니까 용건만 간단히 하세요\n ex)@piano_bot 명령어, 안녕하세요")
        return
    return


slack_token = 'xoxb-347903685010-HIMaKsbqbiH4vNiVS8PjqcMA'
sc = SlackClient(slack_token)

if sc.rtm_connect():
    while True:
        recive_data = sc.rtm_read()

        if len(recive_data):
            keys = list(recive_data[0].keys())
            if 'type' in keys and 'text' in keys and 'user' in keys:
                text = recive_data[0]['text']
                print(text)
                acitve_bot(text)
        #time.sleep(1)
else:
    print("Connection Failed!")
