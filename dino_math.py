import streamlit as st
import random
import json

# === НАСТРОЙКИ И СТИЛИ ===
st.set_page_config(page_title="Дино-Академия", page_icon="🦖", layout="wide")

st.markdown("""
<style>
    .main {background-color: #f0f9e8;}
    .dino-title {font-size: 42px; text-align: center; color: #2e7d32; margin-bottom: 5px;}
    .correct {color: #2e7d32; font-weight: bold; font-size: 20px;}
    .wrong {color: #c62828; font-weight: bold; font-size: 20px;}
    
    /* Стили для имитации тетради в клеточку */
    .notebook-grid {
        background-image: 
            linear-gradient(#cce5ff 1px, transparent 1px),
            linear-gradient(90deg, #cce5ff 1px, transparent 1px);
        background-size: 20px 20px;
        background-color: #fff;
        border: 2px solid #aaa;
        padding: 20px;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
        font-size: 24px;
        line-height: 1.5;
        white-space: pre;
        overflow-x: auto;
        box-shadow: 3px 3px 10px rgba(0,0,0,0.1);
    }
    
    .step-box {
        background-color: #fffde7;
        border-left: 5px solid #fbc02d;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
        font-size: 18px;
    }
</style>
""", unsafe_allow_html=True)

# === ЗАГОЛОВОК ===
st.markdown('<div class="dino-title">🦕 ДИНО-АКАДЕМИЯ 🦖</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center; color:#555; margin-bottom:20px;">Помоги Насте собрать скелет динозавра!</div>', unsafe_allow_html=True)

# === СОСТОЯНИЕ И ПРОГРЕСС ===
if 'progress' not in st.session_state:
    try:
        with open('nastya_progress.json', 'r', encoding='utf-8') as f:
            st.session_state.progress = json.load(f)
    except:
        st.session_state.progress = {'mult_correct': 0, 'mult_total': 0, 'div_correct': 0, 'div_total': 0, 'bones': 0}

def save_progress():
    with open('nastya_progress.json', 'w', encoding='utf-8') as f:
        json.dump(st.session_state.progress, f, ensure_ascii=False, indent=2)

# === БОКОВАЯ ПАНЕЛЬ ===
with st.sidebar:
    st.header("📊 Прогресс Насти")
    p = st.session_state.progress
    st.metric("🦴 Костей", p['bones'])
    st.metric("✅ Умножение", f"{p['mult_correct']}/{p['mult_total']}")
    st.metric("➗ Деление", f"{p['div_correct']}/{p['div_total']}")
    
    total = p['mult_total'] + p['div_total']
    correct = p['mult_correct'] + p['div_correct']
    if total > 0:
        st.progress(correct / total)
        st.caption(f"Точность: {int((correct/total)*100)}%")
    
    st.divider()
    if st.button("🔄 Сбросить"):
        st.session_state.progress = {'mult_correct': 0, 'mult_total': 0, 'div_correct': 0, 'div_total': 0, 'bones': 0}
        save_progress()
        st.rerun()

tab1, tab2, tab3 = st.tabs(["🎯 Умножение", "✏️ Деление в столбик", "🦕 Коллекция"])

# === ВКЛАДКА 1: УМНОЖЕНИЕ ===
with tab1:
    st.header("Тренируй когти! ⚡")
    if 'mult_task' not in st.session_state or st.button("Новое задание", key="new_mult"):
        a, b = random.randint(2,9), random.randint(2,9)
        st.session_state.mult_task = {'a': a, 'b': b, 'ans': a*b}
    
    t = st.session_state.mult_task
    st.markdown(f"### {t['a']} × {t['b']} = ?")
    ans = st.number_input("Ответ:", min_value=0, max_value=100, key="in_mult")
    
    if st.button("Проверить ✅", key="chk_mult"):
        p = st.session_state.progress
        p['mult_total'] += 1
        if ans == t['ans']:
            p['mult_correct'] += 1; p['bones'] += 1
            st.success("🎉 Правильно! +1 кость!")
            if p['mult_correct'] % 5 == 0: st.balloons()
        else:
            st.error(f"❌ Неверно. Ответ: {t['ans']}")
        save_progress(); st.session_state.mult_task = None; st.rerun()

# === ВКЛАДКА 2: ДЕЛЕНИЕ В СТОЛБИК ===
with tab2:
    st.header("Раскопки: учимся делить в столбик! ⛏️")
    st.caption("Приложение будет вести тебя шаг за шагом. Смотри на 'тетрадь' и отвечай на вопросы.")
    
    # Генерация нового примера
    if 'div_state' not in st.session_state or st.button("Начать новый пример", key="new_div_ex"):
        divisor = random.choice([2, 3, 4, 5])  # Начинаем с простых делителей
        quotient = random.randint(12, 45)
        dividend = divisor * quotient
        
        # Подготовка состояния для пошагового решения
        st.session_state.div_state = {
            'dividend': dividend,
            'divisor': divisor,
            'quotient': quotient,
            'digits': str(dividend),
            'current_idx': 0,       # Какую цифру делим сейчас
            'remainder': 0,         # Текущий остаток
            'quotient_str': '',     # То, что уже написали в ответе
            'step_text': '',        # Текст текущего шага
            'visual_lines': [],     # Линии для визуализации столбика
            'finished': False,
            'waiting_for': None     # Что ждём от пользователя: 'q_digit' или 'product'
        }
    
    state = st.session_state.div_state
    
    # --- ЛОГИКА ШАГОВ ---
    if not state['finished']:
        d_str = state['digits']
        idx = state['current_idx']
        rem = state['remainder']
        
        # Формируем текущее число для деления
        current_num = rem * 10 + int(d_str[idx])
        
        # ОПРЕДЕЛЯЕМ, ЧТО ДЕЛАТЬ НА ЭТОМ ШАГЕ
        if state['waiting_for'] is None:
            # ШАГ 1: Найти цифру частного
            q_digit = current_num // state['divisor']
            remainder = current_num % state['divisor']
            
            state['step_text'] = f"Шаг {idx+1}: Делим {current_num} на {state['divisor']}. Сколько раз {state['divisor']} помещается в {current_num}?"
            state['waiting_for'] = 'q_digit'
            state['temp_q'] = q_digit
            state['temp_rem'] = remainder
            
        elif state['waiting_for'] == 'q_digit':
            # Пользователь ввёл цифру частного. Теперь просим произведение.
            state['step_text'] = f"Верно! Теперь умножь {state['divisor']} на {state['temp_q']}. Сколько получится?"
            state['waiting_for'] = 'product'
            
        elif state['waiting_for'] == 'product':
            # Проверили произведение. Теперь вычитаем и сносим.
            product = state['temp_q'] * state['divisor']
            new_rem = state['temp_rem']
            
            # Добавляем строки в визуализацию
            indent = " " * (len(d_str) - idx - 1) 
            
            # Строка с произведением (подчеркиваем)
            prod_str = str(product).rjust(len(str(current_num)))
            state['visual_lines'].append(f"{indent}{prod_str}  <- ({state['divisor']} × {state['temp_q']})")
            state['visual_lines'].append(f"{indent}{'-'*len(str(current_num))}")
            
            # Строка с остатком
            rem_str = str(new_rem).rjust(len(str(current_num)))
            state['visual_lines'].append(f"{indent}{rem_str}  <- Остаток")
            
            # Переход к следующей цифре
            state['remainder'] = new_rem
            state['quotient_str'] += str(state['temp_q'])
            state['current_idx'] += 1
            state['waiting_for'] = None
            
            if state['current_idx'] >= len(d_str):
                state['finished'] = True
                state['step_text'] = " УРА! Пример решён!"
            else:
                state['step_text'] = f"Отлично! Сносим следующую цифру ({d_str[state['current_idx']]}). Получилось {new_rem}{d_str[state['current_idx']]}. Делим это на {state['divisor']}."

    # --- ВИЗУАЛИЗАЦИЯ (ТЕТРАДЬ) ---
    st.markdown('<div class="notebook-grid">', unsafe_allow_html=True)
    
    # Рисуем верхнюю часть столбика (статичную)
    div_len = len(str(state['divisor']))
    did_len = len(str(state['dividend']))
    
    top_line = f"  {state['dividend']} | {state['divisor']}"
    second_line = f"  {'.'*did_len} |__"
    third_line = f"  {state['quotient_str']:<{did_len}}" # Частное пока неполное
    
    st.write(top_line)
    st.write(second_line)
    st.write(third_line)
    st.write("") # Пустая строка
    
    # Рисуем динамические шаги
    for line in state['visual_lines']:
        st.write(line)
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- ПОЛЕ ВВОДА И КНОПКИ ---
    st.markdown(f'<div class="step-box">💬 {state["step_text"]}</div>', unsafe_allow_html=True)
    
    if not state['finished']:
        user_ans = st.number_input("Твой ответ:", min_value=0, max_value=999, key="div_input_step")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("OK 👍", key="div_ok_step"):
                p = st.session_state.progress
                
                if state['waiting_for'] == 'q_digit':
                    if user_ans == state['temp_q']:
                        pass 
                    else:
                        st.error(f"Не совсем. {state['divisor']} помещается в {current_num} ровно {state['temp_q']} раз.")
                        st.info("Попробуй ещё раз!")
                        st.stop()

                elif state['waiting_for'] == 'product':
                    expected_prod = state['temp_q'] * state['divisor']
                    if user_ans == expected_prod:
                        pass
                    else:
                        st.error(f"Ошибка в умножении. {state['divisor']} × {state['temp_q']} = {expected_prod}")
                        st.stop()
                
                st.rerun()
                
        with col2:
            if st.button("Подсказка 💡", key="div_hint_step"):
                if state['waiting_for'] == 'q_digit':
                    st.info(f"Вспомни таблицу умножения на {state['divisor']}. Какое число ближе всего к {current_num}, но не больше?")
                else:
                    st.info(f"Просто умножь {state['divisor']} на {state['temp_q']}.")
    
    else:
        # Пример finished
        p = st.session_state.progress
        p['div_total'] += 1
        p['div_correct'] += 1
        p['bones'] += 3
        save_progress()
        st.balloons()
        st.success(f" Молодец! Ты решила пример {state['dividend']} : {state['divisor']} = {state['quotient']}! +3 кости!")
        if st.button("Следующий пример ️", key="next_div_after_finish"):
            st.session_state.div_state = None
            st.rerun()

# === ВКЛАДКА 3: КОЛЛЕКЦИЯ ===
with tab3:
    st.header("Моя коллекция динозавров 🎨")
    bones = st.session_state.progress['bones']
    dinos = [
        {'name': 'Тираннозавр', 'need': 10, 'emoji': '🦖'},
        {'name': 'Трицератопс', 'need': 25, 'emoji': '🦕'},
        {'name': 'Стегозавр', 'need': 50, 'emoji': '🦎'},
        {'name': 'Брахиозавр', 'need': 100, 'emoji': '🐉'}
    ]
    cols = st.columns(len(dinos))
    for i, d in enumerate(dinos):
        with cols[i]:
            ok = bones >= d['need']
            st.markdown(f'<div style="text-align:center; font-size:50px; opacity:{1 if ok else 0.3}">{d["emoji"]}</div>', unsafe_allow_html=True)
            st.caption(f"**{d['name']}**\n{'✅ Открыт' if ok else f'🔒 Нужно {d["need"]-bones} костей'}")
    
    st.divider()
    st.metric("🦴 Всего костей", bones)
    st.progress(min(bones/100, 1.0))
