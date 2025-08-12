import gradio as gr
from rag_engine import get_answer_from_gemini

# Sohbet geçmişini tutmak için global bir liste
history = []

def respond(message, chat_history):
    """
    Kullanıcı mesajına RAG motorunu kullanarak cevap verir.
    
    Args:
        message (str): Kullanıcının mesajı.
        chat_history (list): Gradio'nun sohbet geçmişi listesi.
        
    Returns:
        tuple: Güncellenmiş sohbet geçmişi ve boş bir mesaj kutusu.
    """
    try:
        # RAG motorundan cevap alıyoruz.
        bot_response = get_answer_from_gemini(message)
        
        # Gradio sohbet geçmişine ekliyoruz.
        chat_history.append((message, bot_response))
        
        # Güncellenmiş sohbet geçmişini ve boş bir giriş kutusu döndürüyoruz.
        return "", chat_history
    except Exception as e:
        error_message = f"Üzgünüm, cevap oluşturulurken bir hata oluştu: {e}"
        chat_history.append((message, error_message))
        return "", chat_history

# Gradio arayüzünü oluşturma
with gr.Blocks(theme=gr.themes.Monochrome()) as demo:
    gr.Markdown("# VEX Robotics Chatbot")
    gr.Markdown("VEX Robotics 2025-2026 'Push Back' oyun kuralları hakkında bana soru sorabilirsin. **Örn: Robot ağırlık sınırı nedir?**")
    
    chatbot = gr.Chatbot(label="VEX Robotics Asistanı")
    msg = gr.Textbox(placeholder="Sorunuzu buraya yazın...", label="Mesajınız")
    
    # Butonları oluşturma
    with gr.Row():
        clear_btn = gr.Button("Sohbeti Temizle", variant="secondary")
        send_btn = gr.Button("Gönder", variant="primary")
        
    # Olayları bağlama
    # Gönder butonuna basıldığında veya enter'a basıldığında `respond` fonksiyonunu çalıştırır.
    send_btn.click(respond, inputs=[msg, chatbot], outputs=[msg, chatbot])
    msg.submit(respond, inputs=[msg, chatbot], outputs=[msg, chatbot])
    
    # Sohbeti temizleme butonu
    clear_btn.click(lambda: None, None, chatbot, queue=False)

# Uygulamayı başlatma
if __name__ == "__main__":
    demo.launch()