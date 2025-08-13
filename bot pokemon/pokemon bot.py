import pyautogui
import cv2
import numpy as np
import pytesseract
import time
import pyperclip
import os

# ====== CONFIGURAÇÕES ======
# Caminho do Tesseract (se precisar no Windows)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Template do Google (logo recortado)
TEMPLATE_PATH = "google_logo_template.png"
template = cv2.imread(TEMPLATE_PATH, cv2.IMREAD_GRAYSCALE)
if template is None:
    print(f"ERRO: Não foi possível carregar o template '{TEMPLATE_PATH}'")
    exit()

# Região onde o Pokémon aparece no Discord
DISCORD_REGION = (475, 705, 390, 249)  # (x, y, largura, altura)

# ====== FUNÇÕES ======

def carregar_imagem_pokemon(caminho_imagem):
    """Cola o caminho do arquivo e confirma a busca"""
    time.sleep(1)  # Espera a janela estar pronta
    pyautogui.press("enter")
    time.sleep(0.5)
    pyperclip.copy(caminho_imagem)
    pyautogui.hotkey("ctrl", "v")  # Cola o caminho
    time.sleep(0.5)
    pyautogui.press("enter")
    print("📸 Imagem do Pokémon carregada para pesquisa!")

def capturar_pokemon():
    """Captura a área do Pokémon no Discord e salva"""
    screenshot = pyautogui.screenshot(region=DISCORD_REGION)
    screenshot.save("pokemon_screenshot.png")
    print("📸 Screenshot do Pokémon salva como 'pokemon_screenshot.png'")

def check_orb_match(screenshot_gray, template_gray, min_matches=20):
    """Verifica similaridade usando ORB"""
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(template_gray, None)
    kp2, des2 = orb.detectAndCompute(screenshot_gray, None)

    if des1 is None or des2 is None:
        return False

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    return len(matches) >= min_matches

def check_ocr_text(screenshot, keywords):
    """Verifica se algum texto esperado está na tela"""
    text = pytesseract.image_to_string(screenshot, lang="por+eng")
    text = text.lower()
    return any(keyword.lower() in text for keyword in keywords)

def is_google_screen():
    """Combina ORB + OCR para confirmar se é a tela do Google"""
    screenshot = pyautogui.screenshot()
    img_bgr = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    orb_result = check_orb_match(img_gray, template)
    ocr_result = check_ocr_text(img_bgr, ["Google", "Pesquisa Google"])

    print(f"ORB: {orb_result} | OCR: {ocr_result}")
    return orb_result or ocr_result

def clicar_icone_busca():
    """Localiza e clica no ícone de busca por imagem"""
    icone_path = "icone_busca.png"  # Salve sua imagem como esse nome na pasta
    pos = pyautogui.locateCenterOnScreen(icone_path, confidence=0.8)
    if pos:
        pyautogui.moveTo(pos)
        pyautogui.click()
        print("🖱️ Ícone de busca clicado!")
        return True
    else:
        print("❌ Ícone não encontrado.")
        return False

# ====== FLUXO PRINCIPAL ======
print("Aguardando 1 segundos para capturar o Pokémon...")
time.sleep(1)
capturar_pokemon()

print("Procurando a tela do Google...")
tentativas = 0
while True:
    tentativas += 1
    if is_google_screen():
        print("✅ Tela do Google detectada!")
        if clicar_icone_busca():
            carregar_imagem_pokemon(r"C:\Users\alex\Desktop\pokemon_screenshot.png")
        break
    else:
        print(f"❌ Não é a tela do Google. Tentando novamente... ({tentativas})")
        pyautogui.hotkey('alt', 'tab')
        time.sleep(0.8)  # tempo para alternar a janela
