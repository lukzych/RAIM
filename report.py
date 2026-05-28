import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas

def generate_pdf(latency_ecg, latency_bvp, latency_eda):
        plt.figure(figsize=(10, 4))
        plt.plot(latency_ecg, label='ECG', color='blue')
        plt.plot(latency_bvp, label='BVP', color='green')
        plt.plot(latency_eda, label='EDA', color='red')
        
        plt.xlabel('Iteracja')
        plt.ylabel('Latencja [s]')
        plt.title('Latencja sensorów w czasie')
        plt.legend()
        plt.savefig('latency_chart.png')
        plt.close()
        

        c = canvas.Canvas("report.pdf")
        c.drawString(250,800, "Raport")
        c.drawString(400,800, "Lukasz Zych")
        c.drawString(400,780, "Rafal Kruszewski")
        c.drawString(100,700, "Pomiary latencji")
        c.drawImage('latency_chart.png', 50, 350, width=500, height=300)
        c.drawString(50, 330, "Latencja w systemie agregacji danych z wielu sensorów " \
        "to czas miedzy momentem gdy sensor ")
        c.drawString(50, 315,"wygenerowal probke a momentem gdy dane zostaly wyslane " \
        "do odbiorcy")

        c.drawString(50,300, "W tym projekcie latencja jest symulowana przez losowe " \
        "opoznienie random_delay dodawane do ")
        c.drawString(50,285, "bazowego interwalu 100ms kazdego watku, reprezentuje niestabilnosc " \
        "lacza miedzy")
        c.drawString(50,270, "sensorem a serwerem, w rzeczywistych systemach " \
        "latencja zalezy od np. jakosci polaczenia")
        c.drawString(50, 225, "Packet loss - utrata pakietow, wystepuje gdy dane nie zostaly " \
        "wyslane do odbiorcy")
        c.drawString(50,210, "W systemach czasu rzeczywistego utrata pakietow powoduje przerwy" \
        " w sygnale ")
        c.drawString(50,195, "Offset przesuwa sie dalej wiec po kilku iteracjach znowu pokaze")
        c.drawString(50,180,"podobnego momentu czasowego")
        c.drawString(50, 150, "Deadlock (zakleszczenie) - wystepuje gdy watki wzajemnie blokuja sobie dostep")
        c.drawString(50, 135, "do wspoldzielonych zasobow i czekaja na zwolnienie blokady.")
        c.drawString(50, 120, "W efekcie aplikacja calkowicie sie zawiesza i przestaje przetwarzac dane.")
        c.drawString(50, 105, "W tym projekcie aby uniknac zakleszczen zastosowano kolejke (Queue),")
        c.drawString(50, 90, "ktora bezpiecznie zarzadza przeplywem danych miedzy sensorami a serwerem.")
        c.save()