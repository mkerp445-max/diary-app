import pandas as pd
import os
from datetime import datetime,timedelta


FILE_NAME = 'diary.csv'

def check_file_exists(file_name):
    #ファイルの存在を確認し、なければメッセージを表示する
    if not os.path.isfile(file_name):
        print(f'{file_name} が見つかりません。')
        return False
    return True


def get_status_input(label):
    #体調や気分など、特定の項目の点数とメモを受け取る

    print(f'\n---{label}の入力---')
    while True:
        try:
            score = int(input(f'{label}を５段階で評価してください（悪い１←   →５良い):\n')) 
            if score  < 1 or  score > 5:
               print('１から５で入力してください')
            else:
               break

        #予定していない入力
        except ValueError:
            print('【エラー】半角英数字で入力')

    return score

def get_time_input(label):
    #４桁の数字を入力させてHH:MM形式に変換して返す

    print(f'--- {label}の入力---')
    while True:
        t_input = input(f'{label}を４桁で入力してください（例：2330）：\n')

        #桁数と数字のチェック
        if len(t_input) != 4 or not t_input.isdigit():
            print('【エラー】4桁の数字（半角）で入力してください')
            continue
    
        hh = t_input[:2]
        mm = t_input[2:]

         #時間として妥当かチェック
        if int(hh) > 23 or int(mm) > 59:
            print('【エラー】正しい時間を入力してください（00:00-23:59）')
            continue

        return f'{hh}:{mm}'

def calculate_sleep_duration(sleep_time,wake_time):
    #hh:mm 形式の就寝・起床時刻から、睡眠時間を計算する
    fmt = '%H:%M'
    s_dt = datetime.strptime(sleep_time,fmt)
    w_dt = datetime.strptime(wake_time,fmt)

    #起床が就寝より前なら、起床を翌日にする(就寝23:00起床07:00)
    if w_dt <= s_dt:
        w_dt += timedelta(days=1)

    duration = w_dt - s_dt
    #秒単位で取得して時間(float)に直す（例7時間30分　-> 7.5)
    return duration.total_seconds() / 3600


def ask_choice(label,choices):
    #選択肢のリストを表示して、選ばれた値を返す共通パーツ
    print(f"\n--- {label}を選択 ---")
    for i,choice in enumerate(choices,start=1):
        print(f'{i}:{choice}{label}')

    while True:
        try:
            idx = int(input("番号を入力してください: "))
            return choices[idx - 1]
        except (ValueError, IndexError): #値と範囲外のエラー
            print("【エラー】正しい番号を入力してください。")
   

def select_diary_date(df):
    #保存データから年・月・日を段階的に選ばせて、特定の日付(w_date)を返す
    if df.empty:
        print("データがありません。")
        return None

    # 年を選ぶ
    years = sorted(df['w_date'].str[:4].unique()) #unique()重複を避ける
    selected_year = ask_choice('年',years)
    
    #月を選ぶ
    df_year = df[df['w_date'].str.startswith(selected_year)] #selected_yearで拾った数字で始まるものを検索
    months = sorted(df_year['w_date'].str[4:6].unique())
    selected_month = ask_choice('月',months)

    #日を選ぶ
    search_key = selected_year + selected_month
    df_month = df[df['w_date'].str.startswith(search_key)]
    days = sorted(df_month['w_date'].str[6:8].unique())
    selected_day = ask_choice('日',days)
    
    return selected_year + selected_month + selected_day # 最終的な8桁の日付を返す


#メインメニュー    
def main():
   # import os
    #print(f"現在の作業場所: {os.getcwd()}")
    #print(f"探しているファイル名: {FILE_NAME}")
    while True:
        print('=============')
        print(' 0:メニュー\n 1:日記を書く\n 2:日記を読む\n 3:日記を削除する\n 9:終了')
        menu = input('番号を入力してください:\n')

        if menu == '1':
            write_diary()

        elif menu == '2':
            read_diary()

        elif menu == '3':
            delete_diary()
        
        elif menu == '9':
            print('終了します')
            break

        else:
            print('正しく入力してください')


def write_diary():
    #日付の入力
    while True:
        
        w_date = input('日付を入力してください（（例）20260330）:\n') 

        if len(w_date) != 8:
            print('【エラー】8桁(例:20260330)で入力してください')
            continue #ループの最初に戻る

        try:
            dt = datetime.strptime(w_date,'%Y%m%d')
            
            year = w_date[0:4]
            month = w_date[4:6]
            day = w_date[6:8]

            confirm = input(f'{year}年{month}月{day}日でいいですか？（y/n）')
            if confirm == 'y':
                break
            else:
                print('もう一度、日付の入力からやり直します')
        except ValueError:
            print('【エラー】存在しない日付です')
   
    # 生活リズムの入力
    sleep_time = get_time_input('就寝時刻')
    wake_time = get_time_input('起床時刻')    
    
    #体調・気分の入力
    w_condition = get_status_input('体調')
    w_mood = get_status_input('気分')
 
    #日記の記入
    print('今日の出来事（空行で終了）')
    lines = []

    while True:
        line = input()
        if line == "": #空行でブレイク
            break
        lines.append(line.replace(',', '、')) #「,」を「、」に変換（データの取り扱い時にエラーが出る）
    text = '\n'.join(lines)

    #データの作成
    new_data = pd.DataFrame( #データのパッキング
        [[w_date,sleep_time,wake_time,w_condition,w_mood,text]],
        columns=['w_date','sleep_time','wake_time','w_condition','w_mood','text']) #カラム名

    # 【理想的な書き方】
    if not os.path.isfile(FILE_NAME):
    # ファイルがないなら：新規作成（1日目）
    # index=False は「余計な番号を振らないで」という意味
        new_data.to_csv(FILE_NAME, index=False, encoding='utf-8')
    else:
    # ファイルがあるなら：追記（2日目以降）
    # mode='a'（追加）して、header=False（見出しは2回書かない）にする
        new_data.to_csv(FILE_NAME, mode='a', header=False, index=False, encoding='utf-8')
    print('●生活リズムと日記を保存しました●')


#日記を読む
def read_diary():
    if not check_file_exists(FILE_NAME):
        return 
    
    df = pd.read_csv(FILE_NAME,dtype={'w_date':str})
    while True:
        print('\n--- 閲覧・分析 ---')
        print(' 1:日記を検索して読む')
        print(' 2:体調・気分の統計')
        print(' 9:戻る')

        choice = input('番号を入力してください')

        if choice == '1':
            show_selected_diary(df)

        elif choice == '2':
            show_statistics(df)

        elif choice == '9':
            print('戻ります')
            break

        else:
            print('正しく入力してください')


def show_selected_diary(df):
    selected_date = select_diary_date(df) #選んだ日付を「selected_date」とする
    if selected_date: #selected_dateがあれば
        entry = df[df['w_date']== selected_date] #selected_dateをcsvのw_dateから探して、そのデータを出す

        if not entry.empty:
            s_time = entry['sleep_time'].values[0] #.value[0]で本文だけ取り出す（きれいなデータにする）
            w_time = entry['wake_time'].values[0]
            condition = entry['w_condition'].values[0]
            mood = entry['w_mood'].values[0]
            content = entry['text'].values[0]

            print('\n' + '='*40)
            print(f"【 日付: {selected_date} 】")
            print(f"【 就寝時刻:{s_time} / 起床時刻: {w_time} 】")
            print(f"  体調スコア: {condition} / 5")
            print(f"  気分スコア: {mood} / 5")
            print('【内容】')
            print(content)
            print('='*40 + "\n")

        else:
            print(f"【エラー】{selected_date}のデータが見つかりませんでした")


def show_statistics(df):
    if df.empty:
        print("データが足りません。")
        return

    # 数値変換と睡眠時間計算
    df['w_condition'] = pd.to_numeric(df['w_condition']) #.to_numeric()でデータを数値に変換
    df['w_mood'] = pd.to_numeric(df['w_mood'])
    #各行のデータの睡眠時間を計算
    df['sleep_hours'] = df.apply(
        lambda row: calculate_sleep_duration(row['sleep_time'], row['wake_time']), axis=1)

    print('\n' + '★' * 10 + ' 自己分析レポート ' + '★' * 10)
    
    avg_sleep = df['sleep_hours'].mean() #平均値
    print(f'■ 合計記録数: {len(df)} 日')
    print(f'■ 平均睡眠時間: {avg_sleep:.2f} 時間') #小数点第二位まで表示
    print(f'■ 平均体調: {df["w_condition"].mean():.2f} / 平均気分: {df["w_mood"].mean():.2f}')

    # 1. 睡眠と気分の相関
    sleep_mood_corr = df["sleep_hours"].corr(df["w_mood"])
    print(f'■ 睡眠時間と気分の相関係数: {sleep_mood_corr:.2f}')

    if sleep_mood_corr > 0.3:
        print('   → 【分析】睡眠時間が長いほど、気分が良い傾向にあります。睡眠の確保が鍵です！')
    elif sleep_mood_corr < -0.3:
        print('   → 【分析】寝すぎると逆に気分が下がる傾向があるかもしれません。')
    else:
        print('   → 【分析】睡眠時間と気分に直接の関連は見られませんでした。質に注目しましょう。')

    # 2. 体調と気分の相関
    correlation = df['w_condition'].corr(df['w_mood'])
    print(f"■ 体調と気分の相関係数: {correlation:.2f}")
    
    # 3. 絶好調な日の検索
    best_days = df[(df['w_condition'] == 5) & (df['w_mood'] == 5)]
    print(f"■ 心身ともに満点(5点)だった日: {len(best_days)} 日")

    # 4. 直近のコンディション（最後の5件）
    print("\n■ 直近5日間の推移 (体調 / 気分)")
    recent = df.tail(5)
    for _, row in recent.iterrows():
        c_bar = "■" * int(row['w_condition']) + "□" * (5 - int(row['w_condition']))
        m_bar = "■" * int(row['w_mood']) + "□" * (5 - int(row['w_mood']))
        print(f"   {row['w_date']}: 体調 {c_bar} / 気分 {m_bar}")

    print("★" * 32 + "\n")



def delete_diary():
    if not check_file_exists(FILE_NAME):
        return 

    df = pd.read_csv(FILE_NAME,dtype={'w_date':str})

    print("\n--- 削除する日記を選択してください ---")
    selected_date = select_diary_date(df)

    if selected_date:
        confirm = input(f'{selected_date}の日記を本当に削除しますか？(y/n):\n')

        if confirm == 'y':
            df = df[df['w_date'] != selected_date]

            df.to_csv(FILE_NAME, index = False, encoding = 'utf-8')
            print(f'◎{selected_date}の日記を削除しました ◎')

        else:
            print('削除をキャンセルしました')


main()
