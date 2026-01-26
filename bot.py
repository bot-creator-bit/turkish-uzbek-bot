import logging
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import sqlite3
import os

# Bot tokeningizni kiriting
TOKEN = os.getenv("8336134380:AAFBWpbfhY4HdiuVevvXxHjlfqpH3pn-8aE")

logging.basicConfig(level=logging.INFO)

bot = Bot(token="8336134380:AAFBWpbfhY4HdiuVevvXxHjlfqpH3pn-8aE")
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# FSM States
class TestStates(StatesGroup):
    choosing_level = State()
    ready_to_start = State()
    taking_test = State()

# Database yaratish va so'zlarni qo'shish
def init_database():
    conn = sqlite3.connect('language_test.db')
    cursor = conn.cursor()
    
    # Users jadvali
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            level TEXT,
            test_count INTEGER DEFAULT 0
        )
    ''')
    
    # Words jadvali
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT,
            uzbek TEXT,
            turkish TEXT
        )
    ''')
    
    # Test results jadvali
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            level TEXT,
            correct INTEGER,
            incorrect INTEGER,
            test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # So'zlar mavjudligini tekshirish
    cursor.execute("SELECT COUNT(*) FROM words")
    if cursor.fetchone()[0] == 0:
        # A1 daraja so'zlari (200+)
        a1_words = [
            ("salom", "merhaba"), ("xayr", "güle güle"), ("iltimos", "lütfen"),
            ("rahmat", "teşekkür ederim"), ("ha", "evet"), ("yo'q", "hayır"),
            ("kecha", "dün"), ("bugun", "bugün"), ("ertaga", "yarın"),
            ("men", "ben"), ("sen", "sen"), ("u", "o"), ("biz", "biz"),
            ("siz", "siz"), ("ular", "onlar"), ("oila", "aile"), ("ona", "anne"),
            ("ota", "baba"), ("aka", "ağabey"), ("opa", "abla"), ("uy", "ev"),
            ("mashina", "araba"), ("kitob", "kitap"), ("qalam", "kalem"),
            ("daftar", "defter"), ("stol", "masa"), ("stul", "sandalye"),
            ("eshik", "kapı"), ("deraza", "pencere"), ("non", "ekmek"),
            ("suv", "su"), ("choy", "çay"), ("kofe", "kahve"), ("sut", "süt"),
            ("go'sht", "et"), ("baliq", "balık"), ("sabzi", "sebze"),
            ("meva", "meyve"), ("olma", "elma"), ("banan", "muz"),
            ("apelsin", "portakal"), ("uzum", "üzüm"), ("qovun", "kavun"),
            ("tarvuz", "karpuz"), ("pomidor", "domates"), ("bodring", "salatalık"),
            ("piyoz", "soğan"), ("sarimsoq", "sarımsak"), ("kartoshka", "patates"),
            ("sabzi", "havuç"), ("qizil", "kırmızı"), ("ko'k", "mavi"),
            ("sariq", "sarı"), ("yashil", "yeşil"), ("oq", "beyaz"),
            ("qora", "siyah"), ("pushti", "pembe"), ("jigarrang", "kahverengi"),
            ("kulrang", "gri"), ("binafsha", "mor"), ("bir", "bir"),
            ("ikki", "iki"), ("uch", "üç"), ("to'rt", "dört"), ("besh", "beş"),
            ("olti", "altı"), ("yetti", "yedi"), ("sakkiz", "sekiz"),
            ("to'qqiz", "dokuz"), ("o'n", "on"), ("yigirma", "yirmi"),
            ("o'ttiz", "otuz"), ("qirq", "kırk"), ("ellik", "elli"),
            ("oltmish", "altmış"), ("yetmish", "yetmiş"), ("sakson", "seksen"),
            ("to'qson", "doksan"), ("yuz", "yüz"), ("ming", "bin"),
            ("katta", "büyük"), ("kichik", "küçük"), ("yangi", "yeni"),
            ("eski", "eski"), ("yaxshi", "iyi"), ("yomon", "kötü"),
            ("issiq", "sıcak"), ("sovuq", "soğuk"), ("tez", "hızlı"),
            ("sekin", "yavaş"), ("baland", "yüksek"), ("past", "alçak"),
            ("uzun", "uzun"), ("qisqa", "kısa"), ("keng", "geniş"),
            ("tor", "dar"), ("og'ir", "ağır"), ("yengil", "hafif"),
            ("qimmat", "pahalı"), ("arzon", "ucuz"), ("chiroyli", "güzel"),
            ("xunuk", "çirkin"), ("aqlli", "akıllı"), ("ahmoq", "aptal"),
            ("kuchli", "güçlü"), ("zaif", "zayıf"), ("boy", "zengin"),
            ("kambag'al", "fakir"), ("baxtli", "mutlu"), ("g'amgin", "üzgün"),
            ("xursand", "sevinçli"), ("jahldor", "kızgın"), ("qo'rqmoq", "korkmak"),
            ("sevmoq", "sevmek"), ("yoqtirmoq", "beğenmek"), ("yoqtirmaslik", "beğenmemek"),
            ("bormoq", "gitmek"), ("kelmoq", "gelmek"), ("tugatmoq", "durmak"),
            ("o'tirmoq", "oturmak"), ("yotmoq", "yatmak"), ("uxlamoq", "uyumak"),
            ("turmoq", "kalkmak"), ("yugumoq", "koşmak"), ("yugurmoq", "yürümek"),
            ("sakramoq", "atlamak"), ("raqsga tushmoq", "dans etmek"),
            ("qo'shiq aytmoq", "şarkı söylemek"), ("o'qimoq", "okumak"),
            ("yozmoq", "yazmak"), ("tinglalmoq", "dinlemek"), ("ko'rmoq", "görmek"),
            ("eshitmoq", "duymak"), ("hidlamoq", "koklamak"), ("tatib ko'rmoq", "tatmak"),
            ("teginmoq", "dokunmak"), ("gapirmoq", "konuşmak"), ("demoq", "söylemek"),
            ("so'ramoq", "sormak"), ("javob bermoq", "cevap vermek"),
            ("tushunmoq", "anlamak"), ("bilmoq", "bilmek"), ("o'rganmoq", "öğrenmek"),
            ("o'qitmoq", "öğretmek"), ("eslalmoq", "hatırlamak"),
            ("unutmoq", "unutmak"), ("topmoq", "bulmak"), ("yo'qotmoq", "kaybetmek"),
            ("qidirmoq", "aramak"), ("kutmoq", "beklemek"), ("bermoq", "vermek"),
            ("olmoq", "almak"), ("sotmoq", "satmak"), ("sotib olmoq", "satın almak"),
            ("ochmoq", "açmak"), ("yopmoq", "kapatmak"), ("boshlalmoq", "başlamak"),
            ("tugatmoq", "bitirmek"), ("yasalmoq", "yapmak"), ("buzmoq", "bozmak"),
            ("tuzatmoq", "tamir etmek"), ("tozalamoq", "temizlemek"),
            ("ifloslamoq", "kirletmek"), ("yumoq", "yıkamak"), ("quritmoq", "kurutmak"),
            ("dazmollamoq", "ütülemek"), ("tikmoq", "dikmek"), ("kesmoq", "kesmek"),
            ("chizmoq", "çizmek"), ("bo'yamoq", "boyamak"), ("yopishmoq", "yapıştırmak"),
            ("ajratmoq", "ayırmak"), ("birlashtirmoq", "birleştirmek"),
            ("to'ldirmoq", "doldurmak"), ("bo'shatmoq", "boşaltmak"),
            ("yig'moq", "toplamak"), ("tarqatmoq", "dağıtmak"),
            ("sanamoq", "saymak"), ("o'lchamoq", "ölçmek"), ("tortmoq", "çekmek"),
            ("itarmoq", "itmek"), ("ko'tarmoq", "kaldırmak"), ("tushirmoq", "indirmek"),
            ("tashlamoq", "atmak"), ("ushlamoq", "tutmak"), ("qo'yib yubormoq", "bırakmak"),
            ("chaqirmoq", "çağırmak"), ("yubormoq", "göndermek"),
            ("qabul qilmoq", "kabul etmek"), ("rad etmoq", "reddetmek"),
            ("rozilik bilmoq", "razı olmak"), ("buning ustiga", "üstelik"),
            ("boshqa", "başka"), ("yana", "yine"), ("hali", "henüz"),
            ("allaqachon", "zaten"), ("albatta", "mutlaka"), ("ehtimol", "belki"),
            ("balki", "belki de"), ("hech qachon", "asla"), ("doim", "her zaman"),
            ("ba'zan", "bazen"), ("tez-tez", "sık sık"), ("kamdan-kam", "nadiren")
        ]
        
        # A2 daraja so'zlari (200+)
        a2_words = [
            ("maktab", "okul"), ("universitet", "üniversite"), ("o'qituvchi", "öğretmen"),
            ("talaba", "öğrenci"), ("dars", "ders"), ("imtihon", "sınav"),
            ("diplom", "diploma"), ("sertifikat", "sertifika"), ("vazifa", "ödev"),
            ("loyiha", "proje"), ("taqdimot", "sunum"), ("tadqiqot", "araştırma"),
            ("kutubxona", "kütüphane"), ("laboratoriya", "laboratuvar"),
            ("sinf xonasi", "sınıf"), ("auditoriya", "amfi"), ("sport zali", "spor salonu"),
            ("oshxona", "mutfak"), ("yotoqxona", "yurt"), ("mehmonxona", "otel"),
            ("restoran", "restoran"), ("kafe", "kafe"), ("bozor", "pazar"),
            ("do'kon", "dükkan"), ("supermarket", "süpermarket"), ("apteka", "eczane"),
            ("kasalxona", "hastane"), ("shifokor", "doktor"), ("hamshira", "hemşire"),
            ("bemor", "hasta"), ("dori", "ilaç"), ("injeksiya", "iğne"),
            ("operatsiya", "ameliyat"), ("ko'rik", "muayene"), ("tashxis", "teşhis"),
            ("davolash", "tedavi"), ("og'riq", "ağrı"), ("isitma", "ateş"),
            ("yo'tal", "öksürük"), ("tumov", "grip"), ("shamollash", "nezle"),
            ("bosh og'rig'i", "baş ağrısı"), ("qorin og'rig'i", "karın ağrısı"),
            ("tish og'rig'i", "diş ağrısı"), ("orqa og'rig'i", "sırt ağrısı"),
            ("harorat", "sıcaklık"), ("bosim", "tansiyon"), ("yurak", "kalp"),
            ("o'pka", "akciğer"), ("jigar", "karaciğer"), ("buyrak", "böbrek"),
            ("oshqozon", "mide"), ("ichak", "bağırsak"), ("miya", "beyin"),
            ("suyak", "kemik"), ("mushak", "kas"), ("teri", "deri"),
            ("qon", "kan"), ("tomir", "damar"), ("nerv", "sinir"),
            ("ko'z", "göz"), ("quloq", "kulak"), ("burun", "burun"),
            ("og'iz", "ağız"), ("til", "dil"), ("tish", "diş"),
            ("lab", "dudak"), ("yuz", "yüz"), ("bosh", "baş"),
            ("soch", "saç"), ("peshona", "alın"), ("qosh", "kaş"),
            ("kiprik", "kirpik"), ("yonoq", "yanak"), ("jag", "çene"),
            ("bo'yin", "boyun"), ("yelka", "omuz"), ("qo'l", "kol"),
            ("tirsak", "dirsek"), ("bilek", "bilek"), ("barmoq", "parmak"),
            ("tirnoq", "tırnak"), ("ko'krak", "göğüs"), ("qorin", "karın"),
            ("bel", "bel"), ("son", "kalça"), ("oyoq", "ayak"),
            ("tizza", "diz"), ("tovon", "topuk"), ("poshnа", "topuk"),
            ("ish", "iş"), ("kasb", "meslek"), ("lavozim", "pozisyon"),
            ("maosh", "maaş"), ("ish haqi", "ücret"), ("bonuş", "prim"),
            ("nafaqa", "emekli maaşı"), ("ta'til", "tatil"), ("dam olish", "izin"),
            ("ish vaqti", "çalışma saati"), ("soat", "saat"), ("daqiqa", "dakika"),
            ("sekund", "saniye"), ("hafta", "hafta"), ("oy", "ay"),
            ("yil", "yıl"), ("asr", "yüzyıl"), ("ming yillik", "binyıl"),
            ("dushanba", "pazartesi"), ("seshanba", "salı"), ("chorshanba", "çarşamba"),
            ("payshanba", "perşembe"), ("juma", "cuma"), ("shanba", "cumartesi"),
            ("yakshanba", "pazar"), ("yanvar", "ocak"), ("fevral", "şubat"),
            ("mart", "mart"), ("aprel", "nisan"), ("may", "mayıs"),
            ("iyun", "haziran"), ("iyul", "temmuz"), ("avgust", "ağustos"),
            ("sentabr", "eylül"), ("oktabr", "ekim"), ("noyabr", "kasım"),
            ("dekabr", "aralık"), ("bahor", "ilkbahar"), ("yoz", "yaz"),
            ("kuz", "sonbahar"), ("qish", "kış"), ("ob-havo", "hava durumu"),
            ("quyosh", "güneş"), ("oy", "ay"), ("yulduz", "yıldız"),
            ("bulut", "bulut"), ("yomg'ir", "yağmur"), ("qor", "kar"),
            ("do'l", "dolu"), ("shamol", "rüzgar"), ("bo'ron", "fırtına"),
            ("momaqaldiroq", "gök gürültüsü"), ("chaqmoq", "şimşek"),
            ("tuman", "sis"), ("muz", "buz"), ("qirov", "kırağı"),
            ("havо", "hava"), ("harorat", "sıcaklık"), ("namlik", "nem"),
            ("bosim", "basınç"), ("shamol tezligi", "rüzgar hızı"),
            ("transport", "ulaşım"), ("avtobus", "otobüs"), ("tramvay", "tramvay"),
            ("metro", "metro"), ("taksi", "taksi"), ("poezd", "tren"),
            ("samolyot", "uçak"), ("kema", "gemi"), ("qayiq", "tekne"),
            ("velosiped", "bisiklet"), ("mototsikl", "motosiklet"),
            ("yuk mashinasi", "kamyon"), ("ambulans", "ambulans"),
            ("o't o'chirish mashinasi", "itfaiye"), ("politsiya mashinasi", "polis arabası"),
            ("bekаt", "durak"), ("stansiya", "istasyon"), ("aeroport", "havalimanı"),
            ("port", "liman"), ("yo'l", "yol"), ("ko'cha", "sokak"),
            ("xiyobon", "cadde"), ("maydon", "meydan"), ("ko'prik", "köprü"),
            ("tunnel", "tünel"), ("svetofor", "trafik ışığı"),
            ("piyodalar o'tish joyi", "yaya geçidi"), ("yo'l belgisi", "trafik işareti"),
            ("haydash guvohnomasi", "ehliyet"), ("yo'lovchi", "yolcu"),
            ("haydovchi", "şöför"), ("chipta", "bilet"), ("narx", "fiyat"),
            ("chegirma", "indirim"), ("to'lov", "ödeme"), ("naqd pul", "nakit"),
            ("plastik karta", "kredi kartı"), ("kvitаntsiya", "makbuz"),
            ("hisob-faktura", "fatura"), ("soliq", "vergi"), ("bank", "banka"),
            ("hisob raqam", "hesap numarası"), ("kredit", "kredi"),
            ("qarz", "borç"), ("foiz", "faiz"), ("valyuta", "döviz"),
            ("kurs", "kur"), ("ayirboshlash", "değiştirme")
        ]
        
        # B1 daraja so'zlari (200+)
        b1_words = [
            ("davlat", "devlet"), ("hukumat", "hükümet"), ("prezident", "cumhurbaşkanı"),
            ("bosh vazir", "başbakan"), ("vazir", "bakan"), ("parlament", "meclis"),
            ("deputat", "milletvekili"), ("saylov", "seçim"), ("ovoz berish", "oy vermek"),
            ("partiya", "parti"), ("siyosat", "siyaset"), ("demokratiya", "demokrasi"),
            ("respublika", "cumhuriyet"), ("monarxiya", "monarşi"), ("konstitutsiya", "anayasa"),
            ("qonun", "kanun"), ("huquq", "hak"), ("burch", "görev"),
            ("erkinlik", "özgürlük"), ("adolat", "adalet"), ("sud", "mahkeme"),
            ("sudya", "yargıç"), ("advokat", "avukat"), ("prokuror", "savcı"),
            ("guvoh", "tanık"), ("ayblov", "suçlama"), ("hukm", "karar"),
            ("jazo", "ceza"), ("qamoq", "hapishane"), ("jarima", "para cezası"),
            ("jinoyat", "suç"), ("jinoyatchi", "suçlu"), ("politsiya", "polis"),
            ("tergovchi", "dedektif"), ("tergov", "soruşturma"), ("ish", "dava"),
            ("iqtisodiyot", "ekonomi"), ("biznes", "iş"), ("savdo", "ticaret"),
            ("eksport", "ihracat"), ("import", "ithalat"), ("bozor", "pazar"),
            ("raqobat", "rekabet"), ("monopoliya", "tekel"), ("korxona", "işletme"),
            ("kompaniya", "şirket"), ("korporatsiya", "kurum"), ("firma", "firma"),
            ("tashkilot", "organizasyon"), ("direktor", "müdür"), ("menejer", "yönetici"),
            ("rahbar", "lider"), ("xodim", "çalışan"), ("ishchi", "işçi"),
            ("mutaxassis", "uzman"), ("professional", "profesyonel"),
            ("malaka", "yeterlilik"), ("tajriba", "deneyim"), ("ko'nikma", "beceri"),
            ("bilim", "bilgi"), ("ma'lumot", "veri"), ("axborot", "bilgi"),
            ("yangilik", "haber"), ("voqea", "olay"), ("hodisa", "hadise"),
            ("muammo", "sorun"), ("masala", "mesele"), ("savol", "soru"),
            ("javob", "cevap"), ("yechim", "çözüm"), ("taklif", "öneri"),
            ("fikr", "fikir"), ("g'oya", "fikir"), ("tushuncha", "kavram"),
            ("nazariya", "teori"), ("amaliyot", "uygulama"), ("tajriba", "deney"),
            ("natija", "sonuç"), ("xulosа", "sonuç"), ("sabab", "sebep"),
            ("oqibat", "sonuç"), ("ta'sir", "etki"), ("qaror", "karar"),
            ("tanlov", "seçim"), ("imkoniyat", "fırsat"), ("xavf", "risk"),
            ("xavfsizlik", "güvenlik"), ("himoya", "koruma"), ("mudofaa", "savunma"),
            ("hujum", "saldırı"), ("urush", "savaş"), ("tinchlik", "barış"),
            ("shartnoma", "anlaşma"), ("kelishuv", "anlaşma"), ("ittifoq", "ittifak"),
            ("hamkorlik", "işbirliği"), ("yordam", "yardım"), ("qo'llab-quvvatlash", "destek"),
            ("tashabbuskorlik", "girişimcilik"), ("korxana ochish", "iş kurmak"),
            ("strategiya", "strateji"), ("rejalashtirish", "planlama"),
            ("boshqarish", "yönetim"), ("nazorat", "kontrol"), ("tahlil", "analiz"),
            ("baholash", "değerlendirme"), ("monitoring", "izleme"),
            ("optimallashtirish", "optimize etme"), ("modernizatsiya", "modernizasyon"),
            ("innovatsiya", "inovasyon"), ("yangilik", "yenilik"),
            ("rivojlanish", "gelişme"), ("o'sish", "büyüme"), ("taraqqiyot", "ilerleme"),
            ("inqiroz", "kriz"), ("tanazzul", "gerileme"), ("pasayish", "düşüş"),
            ("ko'tarilish", "yükseliş"), ("barqarorlik", "istikrar"),
            ("o'zgarish", "değişiklik"), ("islohat", "reform"), ("o'zgartirish", "dönüşüm"),
            ("fan", "bilim"), ("texnologiya", "teknoloji"), ("kashfiyot", "keşif"),
            ("ixtiro", "icat"), ("yangilik", "yenilik"), ("taraqqiyot", "ilerleme"),
            ("tadqiqot", "araştırma"), ("eksperiment", "deney"),
            ("laboratoriya", "laboratuvar"), ("uskunа", "ekipman"),
            ("asbob", "araç"), ("qurilma", "cihaz"), ("mashina", "makine"),
            ("mexanizm", "mekanizma"), ("tizim", "sistem"), ("sxema", "şema"),
            ("chizma", "çizim"), ("dizayn", "tasarım"), ("model", "model"),
            ("namuna", "örnek"), ("standart", "standart"), ("norma", "norm"),
            ("talаb", "gereksinim"), ("ko'rsatkich", "gösterge"),
            ("parametr", "parametre"), ("xususiyat", "özellik"), ("sifat", "kalite"),
            ("miqdor", "miktar"), ("hajm", "hacim"), ("og'irlik", "ağırlık"),
            ("uzunlik", "uzunluk"), ("kenglik", "genişlik"), ("balandlik", "yükseklik"),
            ("chuqurlik", "derinlik"), ("qalinlik", "kalınlık"),
            ("diametr", "çap"), ("radius", "yarıçap"), ("perimetr", "çevre"),
            ("yuza", "alan"), ("shakl", "şekil"), ("shakl berish", "biçimlendirme"),
            ("rang", "renk"), ("ton", "ton"), ("soya", "gölge"),
            ("nur", "ışık"), ("zulmat", "karanlık"), ("yorug'lik", "aydınlık"),
            ("qaroñg'ilik", "karanlık"), ("yorqinlik", "parlaklık"),
            ("intensivlik", "yoğunluk"), ("konsentratsiya", "konsantrasyon"),
            ("tuzilish", "yapı"), ("tarkib", "bileşim"), ("element", "element"),
            ("qism", "parça"), ("bo'lak", "bölüm"), ("bo'lim", "kısım"),
            ("bob", "bölüm"), ("paragraf", "paragraf"), ("jumla", "cümle"),
            ("so'z", "kelime"), ("harf", "harf"), ("belgi", "işaret"),
            ("simvol", "sembol"), ("kod", "kod"), ("shifr", "şifre"),
            ("parol", "parola"), ("kalit", "anahtar"), ("qulf", "kilit"),
            ("himoya", "koruma"), ("maxfiylik", "gizlilik"),
            ("shaxsiy ma'lumotlar", "kişisel veriler"), ("avtorizatsiya", "yetkilendirme"),
            ("autentifikatsiya", "kimlik doğrulama"), ("kirish", "giriş"),
            ("chiqish", "çıkış"), ("ro'yxatdan o'tish", "kayıt"),
            ("profil", "profil"), ("hisob", "hesap"), ("foydalanuvchi", "kullanıcı"),
            ("administrator", "yönetici"), ("moderator", "moderatör"),
            ("obunachi", "abone"), ("kuzatuvchi", "takipçi"), ("do'st", "arkadaş"),
            ("tanish", "tanıdık"), ("hamkasb", "meslektaş"), ("sherik", "ortak"),
            ("raqib", "rakip"), ("dushman", "düşman"), ("do'st", "dost"),
            ("mehribon", "cana yakın"), ("samimiy", "samimi"), ("sodiq", "sadık"),
            ("ishonchli", "güvenilir"), ("halol", "dürüst"), ("adolatli", "adil"),
            ("rahmdil", "merhametli"), ("saxiy", "cömert"), ("kamtar", "alçakgönüllü"),
            ("sabr-toqatli", "sabırlı"), ("jasur", "cesur"), ("botir", "kahraman")
        ]
        
        # B2 daraja so'zlari (200+)
        b2_words = [
            ("falsafa", "felsefe"), ("mantiq", "mantık"), ("etika", "etik"),
            ("estetika", "estetik"), ("ontologiya", "ontoloji"), ("epistemologiya", "epistemoloji"),
            ("metafizika", "metafizik"), ("dunyoqarash", "dünya görüşü"),
            ("mafkura", "ideoloji"), ("qadriyat", "değer"), ("axloq", "ahlak"),
            ("odob", "görgü"), ("ma'naviyat", "maneviyat"), ("ruhiyat", "ruhaniyet"),
            ("ong", "bilinç"), ("ongsizlik", "bilinçsizlik"), ("xotira", "hafıza"),
            ("xayol", "hayal"), ("tasavvur", "tasavvur"), ("intuitsiя", "sezgi"),
            ("fikrlash", "düşünme"), ("muhokama qilish", "muhakeme etme"),
            ("analiz qilish", "analiz etme"), ("sintez", "sentez"),
            ("deduktsiya", "tümdengelim"), ("induktsiya", "tümevarım"),
            ("gipoteza", "hipotez"), ("nazariya", "teori"), ("konsepsiya", "konsept"),
            ("paradigma", "paradigma"), ("metodologiya", "metodoloji"),
            ("tamoyil", "ilke"), ("qoida", "kural"), ("qonuniyat", "yasallık"),
            ("kategoriуa", "kategori"), ("tushuncha", "kavram"), ("atama", "terim"),
            ("ta'rif", "tanım"), ("klassifikatsiya", "sınıflandırma"),
            ("tizimlashtirish", "sistemleştirme"), ("umumlashtirish", "genelleme"),
            ("abstraktsiya", "soyutlama"), ("konkretlashtirish", "somutlaştırma"),
            ("modellashtirish", "modelleme"), ("formalizatsiya", "biçimselleştirme"),
            ("psixologiya", "psikoloji"), ("psixika", "psişik"), ("shaxsiyat", "kişilik"),
            ("xarakter", "karakter"), ("temperament", "mizaç"), ("motivatsiya", "motivasyon"),
            ("emotsiya", "duygu"), ("his-tuyg'u", "his"), ("kayfiyat", "ruh hali"),
            ("stres", "stres"), ("tashvish", "endişe"), ("qo'rquv", "korku"),
            ("umid", "umut"), ("ishonch", "güven"), ("shubha", "şüphe"),
            ("irodа", "irade"), ("qaror qat'iyati", "kararlılık"),
            ("majburiyat", "zorunluluk"), ("mas'uliyat", "sorumluluk"),
            ("burch", "görev"), ("vakolat", "yetki"), ("huquq", "hak"),
            ("ijtimoiy", "sosyal"), ("jamiyat", "toplum"), ("guruh", "grup"),
            ("sinflar", "sınıflar"), ("tabaqа", "tabaka"), ("munosabat", "ilişki"),
            ("aloqa", "iletişim"), ("o'zaro ta'sir", "etkileşim"),
            ("hamkorlik", "işbirliği"), ("raqobat", "rekabet"), ("ziddiyat", "çelişki"),
            ("mojaro", "çatışma"), ("kelishmovchilik", "anlaşmazlık"),
            ("nizо", "uyuşmazluk"), ("bahslashtirish", "tartışma"),
            ("kelishuv", "uzlaşma"), ("murosа", "uzlaşma"), ("yarashish", "barışma"),
            ("intilish", "çaba"), ("maqsad", "amaç"), ("niyat", "niyet"),
            ("istаk", "istek"), ("xohish", "arzu"), ("orzu", "hayal"),
            ("rüya", "rüya"), ("orzular", "hayaller"), ("mafkura", "ideal"),
            ("internet", "internet"), ("veb-sayt", "web sitesi"), ("platforma", "platform"),
            ("tarmoq", "ağ"), ("server", "sunucu"), ("aloqa", "bağlantı"),
            ("protokol", "protokol"), ("interfeys", "arayüz"), ("dastur", "program"),
            ("ilova", "uygulama"), ("fayl", "dosya"), ("papka", "klasör"),
            ("arxiv", "arşiv"), ("zaxira nusxa", "yedek"), ("yuklab olish", "indirme"),
            ("yuklash", "yükleme"), ("sinxronizatsiya", "senkronizasyon"),
            ("ma'lumotlar bazasi", "veritabanı"), ("saqlash", "depolama"),
            ("qayta ishlash", "işleme"), ("shifrlab olish", "şifreleme"),
            ("shifr buzish", "şifre çözme"), ("himoya qilish", "koruma"),
            ("xavfsizlik", "güvenlik"), ("zaiflik", "güvenlik açığı"),
            ("xujum", "saldırı"), ("virus", "virüs"), ("zararli dastur", "kötü amaçlı yazılım"),
            ("antivirus", "antivirüs"), ("xash", "karma"), ("brauzer", "tarayıcı"),
            ("qidiruv tizimi", "arama motoru"), ("elektron pochta", "e-posta"),
            ("messenjer", "anlık mesajlaşma"), ("ijtimoiy tarmoq", "sosyal ağ"),
            ("video konferentsiya", "video konferans"), ("onlayn", "çevrimiçi"),
            ("oflayn", "çevrimdışı"), ("real vaqt", "gerçek zamanlı"),
            ("kechikish", "gecikme"), ("o'tkazish qobiliyati", "bant genişliği"),
            ("tezlik", "hız"), ("sig'im", "kapasite"), ("xotira", "bellek"),
            ("protsessor", "işlemci"), ("videokarta", "ekran kartı"),
            ("monitor", "monitör"), ("klaviatura", "klavye"), ("sichqoncha", "fare"),
            ("printer", "yazıcı"), ("skaner", "tarayıcı"), ("veb-kamera", "web kamerası"),
            ("naushnik", "kulaklık"), ("mikrofon", "mikrofon"), ("dinamik", "hoparlör"),
            ("smartfon", "akıllı telefon"), ("planshet", "tablet"),
            ("noutbuk", "dizüstü bilgisayar"), ("kompyuter", "bilgisayar"),
            ("arxitektura", "mimari"), ("dizayn", "tasarım"), ("kompozitsiya", "kompozisyon"),
            ("proporsiya", "oran"), ("simmetriya", "simetri"), ("ritm", "ritim"),
            ("kontrat", "kontrast"), ("uyg'unlik", "harmoni"), ("rangli", "renkli"),
            ("palitra", "palet"), ("tekstura", "doku"), ("perspektiva", "perspektif"),
            ("makon", "uzay"), ("hajm", "hacim"), ("shakl", "form"),
            ("sirtqi ko'rinish", "görünüm"), ("siluet", "siluet"), ("kontur", "kontur"),
            ("ornament", "süsleme"), ("naqsh", "desen"), ("motiv", "motif"),
            ("stil", "stil"), ("uslub", "tarz"), ("yo'nalish", "yön"),
            ("maktab", "okul"), ("davr", "dönem"), ("davr", "çağ"),
            ("san'at", "sanat"), ("ijod", "yaratıcılık"), ("asar", "eser"),
            ("she'riyat", "şiir"), ("nasr", "düzyazı"), ("drama", "dram"),
            ("roman", "roman"), ("hikoya", "hikaye"), ("qissa", "öykü"),
            ("insho", "deneme"), ("maqola", "makale"), ("tadqiqot", "araştırma"),
            ("monografiya", "monografi"), ("dissertatsiya", "tez"),
            ("musiqa", "müzik"), ("kuy", "melodi"), ("ritm", "ritim"),
            ("temp", "tempo"), ("nota", "nota"), ("tovush", "ses"),
            ("chastota", "frekans"), ("timbre", "tını"), ("dinamika", "dinamik"),
            ("garmoniya", "armoni"), ("akkord", "akor"), ("melodiya", "melodi"),
            ("orkestr", "orkestra"), ("xor", "koro"), ("solist", "solist"),
            ("dirijor", "şef"), ("musiqachi", "müzisyen"), ("ijrochi", "icracı"),
            ("bastakor", "besteci"), ("tekst muallifi", "söz yazarı"),
            ("rassomlik", "resim"), ("rasm", "resim"), ("chizma", "çizim"),
            ("eskiz", "taslak"), ("etyud", "etüt"), ("kartina", "tablo"),
            ("peyzaj", "manzara"), ("portret", "portre"), ("natyurmort", "natürmort"),
            ("abstrakt", "soyut"), ("grafika", "grafik"), ("haykallik", "heykel"),
            ("haykal", "heykel"), ("barеl'yef", "kabartma"), ("monument", "anıt"),
            ("arxeologiya", "arkeoloji"), ("antropologiya", "antropoloji"),
            ("etnografiya", "etnografya"), ("tarix", "tarih"), ("tarixshunoslik", "tarih bilimi"),
            ("xronika", "kronik"), ("annals", "yıllıklar"), ("manba", "kaynak"),
            ("arxiv", "arşiv"), ("hujjat", "belge"), ("yodgorlik", "anıt"),
            ("madaniyat", "kültür"), ("an'anа", "gelenek"), ("urf-odat", "örf ve adet"),
            ("marosim", "tören"), ("bayram", "bayram"), ("tantanа", "kutlama"),
            ("folklor", "folklor"), ("afsona", "efsane"), ("mif", "mitos"),
            ("ertak", "masal"), ("topishmoq", "bilmece"), ("maqol", "atasözü"),
            ("geografiya", "coğrafya"), ("kartografiya", "haritacılık"),
            ("topografiya", "topoğrafya"), ("geologiya", "jeoloji"),
            ("klimatologiya", "iklim bilimi"), ("gidrografiya", "hidrografya"),
            ("okeanografiya", "oşinografi"), ("kontinentlar", "kıtalar"),
            ("okeаnlar", "okyanuslar"), ("dengizlar", "denizler"),
            ("ko'llar", "göller"), ("daryolar", "nehirler"), ("tog'lar", "dağlar"),
            ("vodiylar", "vadiler"), ("cho'llar", "çöller"), ("o'rmonlar", "ormanlar"),
            ("dasht", "bozkır"), ("savanna", "savan"), ("tundra", "tundra"),
            ("ekologiya", "ekoloji"), ("biosfera", "biyosfer"), ("ekosistema", "ekosistem"),
            ("biotsenoz", "biyotop"), ("populatsiya", "popülasyon"),
            ("tur", "tür"), ("gen", "gen"), ("evolyutsiya", "evrim"),
            ("seleksiya", "seçilim"), ("mutatsiya", "mutasyon"),
            ("genetika", "genetik"), ("biologiya", "biyoloji"), ("botanika", "botanik"),
            ("zoologiya", "zooloji"), ("mikrobiologiya", "mikrobiyoloji")
        ]
        
        # C1 daraja so'zlari (200+)
        c1_words = [
            ("abstraktsiya", "soyutlama"), ("aksioma", "aksiyom"), ("algoritm", "algoritma"),
            ("ambivalentlik", "ikirciklilik"), ("analogiya", "analoji"), ("anomaliya", "anomali"),
            ("antagonizm", "çelişki"), ("apriorlik", "önsel"), ("arbitraj", "tahkim"),
            ("assimilyatsiya", "özümseme"), ("avtarxiya", "otarşi"), ("birokratiya", "bürokrasi"),
            ("demaogogiya", "demagoji"), ("determinizm", "determinizm"), ("dialektika", "diyalektik"),
            ("diskriminatsiya", "ayrımcılık"), ("empirizm", "görgülcülük"),
            ("epistemologiya", "bilgi kuramı"), ("estafeta", "bayrak yarışı"),
            ("evristika", "sezgisel"), ("ekspansiya", "yayılma"), ("ekzistensializm", "varoluşçuluk"),
            ("elita", "seçkin"), ("emansipatsiya", "kurtuluş"), ("episod", "bölüm"),
            ("eroziya", "erozyon"), ("eskalatsiya", "tırmanma"), ("espansiya", "genişleme"),
            ("etos", "ahlak anlayışı"), ("evolyutsiya", "evrim"), ("fenomenologiya", "olgu bilim"),
            ("feodalizm", "feodalizm"), ("fideizm", "inançcılık"), ("formulalar", "formüller"),
            ("fundamentalizm", "köktendincilik"), ("fuziya", "kaynaşma"),
            ("generatsiya", "kuşak"), ("genezis", "oluşum"), ("genosid", "soykırım"),
            ("geopolitika", "jeopolitik"), ("gerontokratiya", "yaşlılar egemenliği"),
            ("giperbola", "abartma"), ("gipoteza", "varsayım"), ("globalizatsiya", "küreselleşme"),
            ("gnostiologiya", "bilgi felsefesi"), ("gomogenlik", "homojenlik"),
            ("gumanizm", "insancılık"), ("garmoniya", "uyum"), ("gegemoniya", "egemenlik"),
            ("genealogiya", "soy bilimi"), ("germetizm", "sızdırmazlık"),
            ("geterogenlik", "heterojenlik"), ("identifikatsiya", "özdeşleştirme"),
            ("ideologiya", "düşün dizgesi"), ("idiomatik", "deyimsel"),
            ("illüstratsiya", "resmleme"), ("illüziya", "yanılsama"),
            ("immunitет", "bağışıklık"), ("imperializm", "emperyalizm"),
            ("implementatsiya", "uygulama"), ("implikatsiya", "gerektirme"),
            ("improvizatsiya", "doğaçlama"), ("inadekvatlik", "uygunsuzluk"),
            ("inkorporatsiya", "birleştirme"), ("innovatsiya", "yenilik"),
            ("inqiroz", "kriz"), ("institutsionalizm", "kurumsalcılık"),
            ("integratsiya", "bütünleşme"), ("intellekt", "akıl"), ("intensifikatsiya", "yoğunlaştırma"),
            ("interaktivlik", "etkileşimlilik"), ("interdistsiplinarlik", "disiplinlerarasılık"),
            ("interpretatsiya", "yorumlama"), ("intuitsiу", "sezgi"),
            ("investitsiya", "yatırım"), ("ironiya", "alay"), ("irratsionallik", "akıldışılık"),
            ("izomorfizm", "biçim özdeşliği"), ("kanonizatsiya", "kurallaştırma"),
            ("kategorik", "koşulsuz"), ("kauzallik", "nedensellik"),
            ("klassifikatsiya", "sınıflama"), ("klişе", "kalıplaşmış"),
            ("kodifikatsiya", "yasalaştırma"), ("kognitivizm", "bilişselcilik"),
            ("kolaboratsiya", "işbirlikçilik"), ("koloniализm", "sömürgecilik"),
            ("komplementarlik", "tamamlayıcılık"), ("komponenta", "bileşen"),
            ("kompozitsiya", "düzenleme"), ("kompromis", "uzlaşma"),
            ("kommunikatsiya", "iletişim"), ("konglomerat", "karma"),
            ("konjunktura", "durum"), ("konnotatsiya", "çağrışım"),
            ("konsensus", "fikir birliği"), ("konstituent", "kurucu"),
            ("konstruktsiya", "yapı"), ("kontekst", "bağlam"), ("kontseptsiya", "tasarı"),
            ("konvergentsiya", "yakınsama"), ("konventsiya", "sözleşme"),
            ("koordinatsiya", "eşgüdüm"), ("korrelyatsiya", "ilişki"),
            ("korroziya", "paslanma"), ("kosmopolitizm", "dünyalılık"),
            ("kreativlik", "yaratıcılık"), ("kritika", "eleştiri"),
            ("kulminatsiya", "doruk"), ("legitimlik", "yasallık"),
            ("liberalizm", "özgürlükçülük"), ("lingvistika", "dil bilimi"),
            ("manifest", "bildiri"), ("marjinallik", "marjinallik"),
            ("materializm", "maddecilik"), ("meritokratiya", "liyakat sistemi"),
            ("metaforа", "eğretileme"), ("metodologiya", "yöntem bilimi"),
            ("migrasiya", "göç"), ("militarizm", "militarizm"),
            ("minimalizm", "azlıkçılık"), ("mobilizatsiya", "seferberlik"),
            ("modal'nost", "kiplik"), ("modernizatsiya", "çağdaşlaşma"),
            ("monetarizm", "parasalcılık"), ("monitorlash", "izleme"),
            ("monopoliya", "tekel"), ("motivatsiya", "güdüleme"),
            ("multikultural", "çokkültürlü"), ("mutatatsiya", "mutasyon"),
            ("natsionalizm", "ulusçuluk"), ("nihilizm", "hiççilik"),
            ("nominalizm", "adcılık"), ("norma", "norm"), ("nostalgia", "özlem"),
            ("nüans", "ince ayrıntı"), ("obektivlik", "nesnellik"),
            ("oligarxiya", "azınlık egemenliği"), ("ontologiya", "varlık bilimi"),
            ("operatsionalizatsiya", "işlemselleştirme"), ("optimizatsiya", "eniyileme"),
            ("ortodoksallik", "tutuculuk"), ("paradigma", "örnek"),
            ("paradoks", "çelişki"), ("parallelizm", "koşutluk"),
            ("parametr", "parametre"), ("parodiya", "taklit"), ("paternalizm", "babacan yönetim"),
            ("patriarxat", "ataerkillik"), ("percepciya", "algılama"),
            ("perspektiva", "bakış"), ("plьuralizm", "çoğulculuk"),
            ("polarizatsiya", "kutuplaşma"), ("populizm", "halkçılık"),
            ("postmodernizm", "postmodernizm"), ("pragmatizm", "faydacılık"),
            ("presedent", "örnek olay"), ("prognoz", "öngörü"),
            ("prогrеss", "ilerleme"), ("propaganda", "propaganda"),
            ("proporsiyonal", "orantılı"), ("protokol", "tutanak"),
            ("provinsiаl", "taşralı"), ("ratsionalizatsiya", "akılcıllaştırma"),
            ("realizm", "gerçekçilik"), ("reduktionizm", "indirgemecilik"),
            ("referens", "gönderme"), ("refleksiya", "yansıtma"),
            ("regress", "gerileme"), ("rehabilitatsiya", "onarım"),
            ("rekonstruktsiya", "yeniden kurma"), ("relativizm", "görecilik"),
            ("relyativizm", "izafilik"), ("renessans", "rönesans"),
            ("reprezentativlik", "temsil edilebilirlik"), ("repressiya", "baskı"),
            ("resurs", "kaynak"), ("retrospektiva", "geriye bakış"),
            ("revolyutsiya", "devrim"), ("ritualizatsiya", "törenselleştirme"),
            ("romantizm", "romantizm"), ("rutina", "alışkanlık"),
            ("segregatsiya", "ayrımlaştırma"), ("selekciya", "seçilim"),
            ("semantika", "anlam bilimi"), ("simvolizm", "simgecilik"),
            ("simulyatsiya", "benzetim"), ("singularlik", "tekillik"),
            ("sintez", "sentez"), ("skeptitsizm", "kuşkuculuk"),
            ("sinergeya", "eşgüdüm"), ("solidarlik", "dayanışma"),
            ("sotsializatsiya", "toplumsallaşma"), ("sotsializm", "sosyalizm"),
            ("spetsifikatsiya", "belirleme"), ("spontannost", "anlıksallık"),
            ("stabilizatsiya", "istikrar"), ("standardizatsiya", "standartlaştırma"),
            ("status-kvo", "mevcut durum"), ("stereotip", "kalıp"),
            ("stigmatizatsiya", "damgalama"), ("stimul", "uyarı"),
            ("stixiyаlik", "kendiliğindenlik"), ("stratifikatsiya", "tabakalanma"),
            ("struktura", "yapı"), ("subjektivlik", "öznellik"),
            ("subordinatsiya", "ast-üst ilişkisi"), ("subsidiya", "sübvansiyon"),
            ("substansiya", "öz"), ("surrogat", "taklit"), ("sintez", "bireşim"),
            ("tabu", "yasak"), ("taxonomiya", "sınıflandırma bilimi"),
            ("telеlogiya", "erekbilim"), ("tolerantlik", "hoşgörü"),
            ("totalitarizm", "bütüncülük"), ("traditsiyanalizm", "gelenekçilik"),
            ("transsendental", "aşkın"), ("transformatsiya", "dönüşüm"),
            ("trend", "eğilim"), ("utilitarizm", "faydacılık"),
            ("utopiya", "ütopya"), ("validlik", "geçerlilik"),
            ("variatsiya", "değişke"), ("verifikatsiya", "doğrulama"),
            ("virtuallik", "sanal"), ("volatillik", "dalgalanma")
        ]
        
        # C2 daraja so'zlari (200+)
        c2_words = [
            ("amalgamatsiya", "birleştirme"), ("ambiguitet", "belirsizlik"),
            ("anakronizm", "çağ dışılık"), ("antiteza", "karşıtlık"),
            ("aperseperatsiya", "bilinçli algılama"), ("aposteriori", "sonsal"),
            ("artеfakt", "yapay nesne"), ("asimptotik", "yaklaşımsal"),
            ("asinkronlik", "eşzamansızlık"), ("avtorefeksivlik", "özdönüşlülük"),
            ("bipolar", "iki kutuplu"), ("bifurkatsiya", "çatallanma"),
            ("demistifikatsiya", "gizgüden arındırma"), ("deonologiya", "ödevbilim"),
            ("derivatsiya", "türetme"), ("desemantizatsiya", "anlamdan yoksunlaşma"),
            ("desinkronizatsiya", "zamandışılaşma"), ("dialektik sintez", "diyalektik bireşim"),
            ("diaxroniya", "ardıllık"), ("dikotomiya", "ikili bölünme"),
            ("dislokatsiya", "yerinden çıkarma"), ("disparitet", "eşitsizlik"),
            ("dissidensiya", "muhalefet"), ("distantsirovannost", "uzak durma"),
            ("divergentsiya", "ıraksaklık"), ("diversifikatsiya", "çeşitlendirme"),
            ("dogmatizm", "katı inançlılık"), ("dualizm", "ikicilik"),
            ("эkstrapolyatsiya", "dış yayım"), ("eksplitsilik", "açıklık"),
            ("elativlik", "üstünlük"), ("empatiya", "özdeşim kurma"),
            ("еmpriokrititsizm", "deneysel eleştiricilik"), ("endemik", "yöresel"),
            ("entropiya", "düzensizlik"), ("epifenomen", "ikincil olgu"),
            ("epistemik", "bilimsel"), ("eskhatologiya", "ahiret bilimi"),
            ("etnosentrizm", "ırkmerkezcilik"), ("evfemizm", "örtmece"),
            ("evristika", "buluş yöntemi"), ("egzegeza", "yorum bilimi"),
            ("falsifikatsiya", "yanlışlama"), ("fatalizm", "kadercilik"),
            ("fenomen", "görüngü"), ("fenotip", "görünüş tipi"),
            ("fragmentatsiya", "parçalanma"), ("funktsionalizm", "işlevselcilik"),
            ("fuziya", "kaynaşma"), ("generalizatsiya", "genelleme"),
            ("geshtalt", "bütünlük"), ("gibridizatsiya", "melezleme"),
            ("giperonim", "üst kavram"), ("giponim", "alt kavram"),
            ("gipostatizatsiya", "özleştirme"), ("gnostitsizm", "gnostisizm"),
            ("gomeopatiya", "benzer tedavi"), ("gomeostaz", "dengelilik"),
            ("grаdiеnt", "değişim"), ("gramatikalizatsiya", "dilbilgiselleşme"),
            ("герменевтika", "yorum bilimi"), ("geterogennost", "türdeş olmama"),
            ("geykologiya", "doğabilim"), ("idiоm", "deyim"), ("idisinкraziya", "özellik"),
            ("illokutiv", "edim gücü"), ("imperativ", "buyurma kipi"),
            ("impersonalizatsiya", "kişisizleştirme"), ("implikatsiya", "çıkarım"),
            ("inаuguratsiya", "göreve başlama"), ("invarіant", "değişmez"),
            ("institutsionalizm", "kurumsalcılık"), ("instrumentalizm", "araçsalcılık"),
            ("intersubjektivlik", "öznelerarasılık"), ("intrinsik", "içkin"),
            ("introjektsiya", "içselleme"), ("intuitsionizm", "seziselcilik"),
            ("irreduktibilnost", "indirgenemezlik"), ("irrelеvantlik", "ilgisizlik"),
            ("isotopiya", "anlam bütünlüğü"), ("iteratsiya", "yineleme"),
            ("juxtapozitsiya", "yan yana koyma"), ("kanonik", "kurallı"),
            ("katarsis", "arınma"), ("kategorik imperativ", "koşulsuz buyruk"),
            ("kauzativlik", "neden olma"), ("kibernetika", "yönetimbilim"),
            ("kinesteziya", "devinim duyusu"), ("kognatsiya", "bilişsellik"),
            ("kolligatsiya", "bağlanma"), ("kollokatsiya", "birlikte kullanım"),
            ("komensurabilnost", "ölçülebilirlik"), ("kommutatsiya", "değiştirim"),
            ("kompatibilnost", "uyumluluk"), ("kompenzatsiya", "denkleştirme"),
            ("komplementarnost", "tamamlayıcılık"), ("konativlik", "istemeye yönelik"),
            ("konsolidatsiya", "sağlamlaştırma"), ("konstellatsiya", "takımyıldız"),
            ("kontaminatsiya", "karıştırma"), ("kontingentlik", "rastlantısallık"),
            ("kontrapunkt", "karşısesleme"), ("kontrafaktik", "gerçekdışı"),
            ("konversiya", "dönüşüm"), ("korrelyativ", "ilişkisel"),
            ("kosmogoniya", "evren oluşum bilimi"), ("leytmotiv", "ana güdü"),
            ("leksikalizatsiya", "sözcükleşme"), ("lingvorekulturologiya", "dil kültür bilimi"),
            ("lokalizatsiya", "yerleştirme"), ("makrostruktura", "üst yapı"),
            ("maksimalizm", "azamcılık"), ("manifеstatsiya", "belirginleşme"),
            ("маргинalizatsiya", "marjinalleşme"), ("mаtritsa", "kalıp"),
            ("memuar", "anı"), ("metafizika", "fizikötesi"), ("metaniva", "üstdüzey"),
            ("metodika", "yöntem"), ("metrika", "ölçü"), ("metonimiya", "ad aktarması"),
            ("mikrostruktura", "altYapı"), ("mimetik", "taklit edici"),
            ("modallik", "kipsellik"), ("modifikatsiya", "değiştirme"),
            ("momenlum", "ivme"), ("morfemа", "biçimbirim"), ("morfologiya", "biçimbilim"),
            ("multiplikatsiya", "çoklama"), ("narrativ", "anlatı"),
            ("naturalizm", "doğalcılık"), ("nominatsiya", "adlandırma"),
            ("номinal", "adsal"), ("noos", "us"), ("normativ", "kuralcı"),
            ("objektivatsiya", "nesneleştirme"), ("okkultizm", "gizcilik"),
            ("omogennost", "homojenlik"), ("omofon", "sesteş"), ("ontogenez", "bireygelişim"),
            ("onomatopoеya", "yansıma söz"), ("operatsionalizatsiya", "işlemselleştirme"),
            ("opportunizm", "fırsatçılık"), ("organitsizm", "organizmacılık"),
            ("ortogonal", "dikgen"), ("oksimоron", "çelişki sanatı"),
            ("paleоntologiya", "eskiçağ bilimi"), ("panteizm", "doğatanrıcılık"),
            ("paradoks", "çelişki"), ("parallelizm", "koşutluk"),
            ("parametrizatsiya", "parametreleme"), ("pardigmatika", "dizge bilgisi"),
            ("paterializm", "maddecilik"), ("patologiya", "hastalık bilimi"),
            ("perfektivlik", "tamamlanmış"),  ("perifrazа", "dolambaçlı anlatım"),
            ("permutatsiya", "yer değiştirme"), ("perpetuum mobile", "sonsuz hareket"),
            ("polemika", "tartışma"), ("polifoniya", "çokseslilik"),
            ("polisemiya", "çokanlamlılık"), ("postulat", "önerme"),
            ("pragmatizm", "faydacılık"), ("predikat", "yüklem"),
            ("prefiksatsiya", "önekle türetme"), ("prepozitsiya", "ilgeç"),
            ("preskriptiv", "buyurucu"), ("presuppozitsiya", "önsav"),
            ("primordial", "ilksel"), ("priorinet", "öncelik"),
            ("procedura", "işlem"), ("prognostik", "öngörücü"),
            ("prolife ratsiya", "çoğalma"), ("propozitsiya", "önerme"),
            ("prospektivlik", "ileriye dönüklük"), ("protоtip", "ilkörnek"),
            ("psevdоnim", "takma ad"), ("radikallik", "köktendincilik"),
            ("ratsionalnost", "akılcılık"), ("reaktivatsiya", "yeniden etkinleştirme"),
            ("retsipient", "alıcı"), ("reduksiya", "indirgeme"),
            ("referensiya", "gönderme"), ("refleksivlik", "dönüşlülük"),
            ("rekursiya", "özyineleme"), ("relativnost", "görecelik"),
            ("remanifestatsiya", "yeniden belirme"), ("restrikciya", "sınırlama"),
            ("retardatsiya", "geciktirme"), ("retrospekciya", "geriye bakış"),
            ("reversibilnost", "geri dönüşümlülük"), ("rigidnost", "katılık"),
            ("ritоrika", "söz sanatı"), ("rudiment", "kalıntı"),
            ("sakralizatsiya", "kutsallaştırma"), ("sankciya", "yaptırım"),
            ("sekularizatsiya", "laikleştirme"), ("seleksiya", "seçme"),
            ("semantizatsiya", "anlamlandırma"), ("semiotika", "göstergebilim"),
            ("sengularizm", "tekilcilik"), ("sinkroniya", "eşzamanlılık"),
            ("sinкretizm", "birleşikcilik"), ("sintaktika", "sözdizimi"),
            ("situativlik", "bağlamsal"), ("skepsis", "kuşku"),
            ("solipsizm", "benmerkezcilik"), ("sonorolik", "seslilük"),
            ("spetsifikatsiya", "özgüleme"), ("spontannost", "kendiliğindenlik"),
            ("staticizm", "durağanlık"), ("stigmatizatsiya", "damgalama"),
            ("stilistika", "biçembilim"), ("stixiynost", "kendiliğindenlik"),
            ("subеkt", "özne"), ("sublimatsiya", "yüceltme"),
            ("subordinatsiya", "altındalık"), ("substantiv", "ad"),
            ("substrat", "altkatman"), ("suffiksatsiya", "sonekle türetme"),
            ("superstruktura", "üstyapı"), ("suppletivizm", "tamamlama"),
            ("surrоgat", "yerine geçen"), ("simvolika", "simge dizgesi"),
            ("taxonomiya", "sınıflandırma bilimi"), ("telos", "erek"),
            ("termіnologiya", "terim bilimi"), ("tesauro", "eşanlamlılar sözlüğü"),
            ("totalizatsiya", "tümelleştirme"), ("transdukciya", "iletim"),
            ("transkriptsiya", "çevriyazı"), ("transliteratsiya", "harf aktarımı"),
            ("transmutatsiya", "dönüşüm"), ("transfiguratsiya", "biçim değiştirme"),
            ("triangulatsiya", "üçgenleme"), ("tropologiya", "eğretileme bilimi"),
            ("typologiya", "tipoloji"), ("unifikatsiya", "birleştirme"),
            ("universalizm", "evrenselcilik"), ("utopizm", "ütopyacılık"),
            ("validatsiya", "geçerlendirme"), ("variabelnost", "değişkenlik"),
            ("verbalizatsiya", "söze dökme"), ("verifikatsionizm", "doğrulamacılık"),
            ("virtualnost", "sanallık"), ("vokalizm", "ünlü dizgesi"),
            ("voluntarizm", "istemcilik"), ("vulgarizm", "kaba söz"),
            ("zigzag", "kıvrım"), ("zoomorvizm", "hayvanlaştırma")
        ]
        # BU YERGA SO'ZLARINGIZNI QO'SHING
        # Masalan:
        # a1_words = [("salom", "merhaba"), ...]
        # for level, words in [('A1', a1_words), ('A2', a2_words), ...]:
        #     for uzb, turk in words:
        #         cursor.execute("INSERT INTO words (level, uzbek, turkish) VALUES (?, ?, ?)", (level, uzb, turk))
        pass
        
    conn.commit()
    conn.close()

# Foydalanuvchini database saqlash
def save_user(user_id, username, level):
    conn = sqlite3.connect('language_test.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, username, level, test_count)
        VALUES (?, ?, ?, COALESCE((SELECT test_count FROM users WHERE user_id = ?), 0))
    ''', (user_id, username, level, user_id))
    conn.commit()
    conn.close()

# Foydalanuvchi ma'lumotlarini olish
def get_user(user_id):
    conn = sqlite3.connect('language_test.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

# Test uchun so'zlarni olish
def get_test_words(level, count=20):
    conn = sqlite3.connect('language_test.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT uzbek, turkish FROM words WHERE level = ? ORDER BY RANDOM() LIMIT ?",
        (level, count)
    )
    words = cursor.fetchall()
    conn.close()
    return words

# Test natijasini saqlash
def save_test_result(user_id, level, correct, incorrect):
    conn = sqlite3.connect('language_test.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO test_results (user_id, level, correct, incorrect)
        VALUES (?, ?, ?, ?)
    ''', (user_id, level, correct, incorrect))
    cursor.execute(
        "UPDATE users SET test_count = test_count + 1 WHERE user_id = ?",
        (user_id,)
    )
    conn.commit()
    conn.close()

# Daraja tanlash tugmalari
def get_level_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="A1 - Boshlang'ich", callback_data="level_A1")],
        [InlineKeyboardButton(text="A2 - Elementar", callback_data="level_A2")],
        [InlineKeyboardButton(text="B1 - O'rta", callback_data="level_B1")],
        [InlineKeyboardButton(text="B2 - O'rta-Yuqori", callback_data="level_B2")],
        [InlineKeyboardButton(text="C1 - Ilg'or", callback_data="level_C1")],
        [InlineKeyboardButton(text="C2 - Mohir", callback_data="level_C2")]
    ])
    return keyboard

# Testni boshlash tugmalari
def get_start_test_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha", callback_data="start_yes"),
            InlineKeyboardButton(text="❌ Yo'q", callback_data="start_no")
        ]
    ])
    return keyboard

# Javob tugmalari
def get_answer_keyboard(options):
    buttons = [[InlineKeyboardButton(text=opt, callback_data=f"answer_{i}")] 
               for i, opt in enumerate(options)]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# /start komandasi
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user = get_user(message.from_user.id)
    
    if user:
        await message.answer(
            f"Xush kelibsiz, {message.from_user.first_name}!\n\n"
            f"Sizning darajangiz: {user[2]}\n"
            f"Topshirgan testlar soni: {user[3]}\n\n"
            f"Yangi test boshlash uchun darajangizni tanlang:",
            reply_markup=get_level_keyboard()
        )
    else:
        await message.answer(
            f"Assalomu alaykum, {message.from_user.first_name}! 🇺🇿🇹🇷\n\n"
            f"O'zbek-Turk tili test botiga xush kelibsiz!\n\n"
            f"Iltimos, o'z darajangizni tanlang:",
            reply_markup=get_level_keyboard()
        )
    await state.set_state(TestStates.choosing_level)

# Daraja tanlash
@dp.callback_query(F.data.startswith("level_"))
async def process_level_selection(callback: types.CallbackQuery, state: FSMContext):
    level = callback.data.split("_")[1]
    await state.update_data(level=level)
    
    save_user(callback.from_user.id, callback.from_user.username, level)
    
    await callback.message.edit_text(
        f"Siz {level} darajasini tanladingiz.\n\n"
        f"Testni boshlashga tayyormisiz?\n"
        f"Test 20 ta savoldan iborat.",
        reply_markup=get_start_test_keyboard()
    )
    await state.set_state(TestStates.ready_to_start)
    await callback.answer()

# Testni boshlash
@dp.callback_query(F.data == "start_yes")
async def start_test(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    level = data.get('level')
    
    # Testni boshlash
    words = get_test_words(level, 20)
    
    if not words:
        await callback.message.edit_text("Xatolik! Ushbu daraja uchun so'zlar topilmadi.")
        await state.clear()
        return
    
    # Test savollarini tayyorlash
    questions = []
    for uzb, turk in words:
        # Tasodifiy yo'nalish: O'zbekcha->Turkcha yoki Turkcha->O'zbekcha
        if random.choice([True, False]):
            question_word = uzb
            correct_answer = turk
            question_type = "uz_tr"
        else:
            question_word = turk
            correct_answer = uzb
            question_type = "tr_uz"
        
        # Noto'g'ri javoblar uchun boshqa so'zlarni olish
        other_words = get_test_words(level, 4)
        wrong_answers = []
        for w in other_words:
            if question_type == "uz_tr":
                if w[1] != correct_answer:
                    wrong_answers.append(w[1])
            else:
                if w[0] != correct_answer:
                    wrong_answers.append(w[0])
            if len(wrong_answers) >= 3:
                break
        
        # Javoblarni aralashtirish
        options = wrong_answers[:3] + [correct_answer]
        random.shuffle(options)
        correct_index = options.index(correct_answer)
        
        questions.append({
            'question': question_word,
            'options': options,
            'correct': correct_index,
            'type': question_type
        })
    
    await state.update_data(
        questions=questions,
        current_question=0,
        correct_answers=0,
        incorrect_answers=0
    )
    
    # Birinchi savolni yuborish
    await send_question(callback.message, state)
    await callback.answer()

@dp.callback_query(F.data == "start_no")
async def cancel_test(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Test bekor qilindi. Qaytadan boshlash uchun /start buyrug'ini yuboring."
    )
    await state.clear()
    await callback.answer()

# Savolni yuborish
async def send_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    questions = data['questions']
    current = data['current_question']
    
    if current >= len(questions):
        # Test tugadi
        await finish_test(message, state)
        return
    
    question = questions[current]
    lang_direction = "🇺🇿 ➡️ 🇹🇷" if question['type'] == "uz_tr" else "🇹🇷 ➡️ 🇺🇿"
    
    text = (
        f"Savol {current + 1}/20 {lang_direction}\n\n"
        f"<b>{question['question']}</b> so'zining tarjimasini toping:"
    )
    
    await message.edit_text(
        text,
        reply_markup=get_answer_keyboard(question['options']),
        parse_mode="HTML"
    )
    await state.set_state(TestStates.taking_test)

# Javobni tekshirish - TO'G'IRLANGAN
@dp.callback_query(F.data.startswith("answer_"))
async def check_answer(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    answer_index = int(callback.data.split("_")[1])
    
    questions = data['questions']  # TO'G'IRLANDI
    current = data['current_question']
    correct_answers = data['correct_answers']
    incorrect_answers = data['incorrect_answers']
    
    question = questions[current]
    
    if answer_index == question['correct']:
        correct_answers += 1
        result = "✅ To'g'ri!"
    else:
        incorrect_answers += 1
        correct_word = question['options'][question['correct']]
        result = f"❌ Noto'g'ri! To'g'ri javob: <b>{correct_word}</b>"
    
    # Keyingi savolga o'tish
    await state.update_data(
        current_question=current + 1,
        correct_answers=correct_answers,
        incorrect_answers=incorrect_answers
    )
    
    await callback.answer(result, show_alert=True)
    await send_question(callback.message, state)

# Testni tugatish
async def finish_test(message: types.Message, state: FSMContext):
    data = await state.get_data()
    correct = data['correct_answers']
    incorrect = data['incorrect_answers']
    level = data['level']
    
    total = correct + incorrect
    percentage = (correct / total * 100) if total > 0 else 0
    
    # Natijani saqlash
    save_test_result(message.chat.id, level, correct, incorrect)
    
    # Baho berish
    if percentage >= 90:
        grade = "A'lo! 🌟"
    elif percentage >= 75:
        grade = "Yaxshi! 👍"
    elif percentage >= 60:
        grade = "Qoniqarli ✅"
    else:
        grade = "Yaxshilanishi kerak 📚"
    
    result_text = (
        f"🎉 <b>Test yakunlandi!</b>\n\n"
        f"📊 <b>Natijalaringiz:</b>\n"
        f"✅ To'g'ri javoblar: {correct}\n"
        f"❌ Noto'g'ri javoblar: {incorrect}\n"
        f"📈 Foiz: {percentage:.1f}%\n\n"
        f"🏆 Baho: {grade}\n\n"
        f"Yangi test boshlash uchun /start buyrug'ini yuboring."
    )
    
    await message.edit_text(result_text, parse_mode="HTML")
    await state.clear()

# AVTOMATIK ISHGA TUSHIRISH
async def on_startup():
    """Bot ishga tushganda avtomatik bajariladi"""
    init_database()
    logging.info("✅ Bot muvaffaqiyatli ishga tushdi!")
    logging.info("📊 Database tayyor!")

# Botni ishga tushirish
async def main():
    init_database()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())