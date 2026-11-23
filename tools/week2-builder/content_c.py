"""Slot C pilots, episode 2 of each candidate.

C1: Hindi horror (original fiction). C2: Hindu epics in English.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "render"))
from storyboards import geo, number, cards, kinetic, atmos  # noqa: E402

S = {
    "wisdomlib_ak18": "https://www.wisdomlib.org/hinduism/book/the-ramayana-of-valmiki/d/doc423965.html",
    "sanskritdocs_ak107": "https://sanskritdocuments.org/sites/valmikiramayan/ayodhya/sarga107/ayodhya_107_prose.htm",
    "wiki_exile": "https://en.wikipedia.org/wiki/Exile_of_Rama",
    "hindutone_trail": "https://hindutone.com/temples/ramayana-places-in-india-trail/",
    "outlook_kishkindha": "https://www.outlooktraveller.com/amp/story/experiences/heritage/ram-navami-footsteps-of-ram-sita-and-lakshman",
    "wiki_adams": "https://en.wikipedia.org/wiki/Adam%27s_Bridge",
    "esa_adams": "https://www.esa.int/ESA_Multimedia/Images/2024/06/Earth_from_Space_Adam_s_Bridge",
    "wiki_rvgp": "https://en.wikipedia.org/wiki/Ram_Van_Gaman_Path",
    "wiki_ramayana": "https://en.wikipedia.org/wiki/Ramayana",
}

# ---- C1: Hindi horror, episode 2 -----------------------------------------------
HORROR = {
    "channel": "c-horror-hi",
    "slug": "naunvi-manzil",
    "format": "long", "lang": "hi",
    "topic": "Original horror story: the lift that stops at the ninth floor",
    "angle": "Modern high-rise, a 3:33 am lift, a guard's register that counts one person too many",
    "cluster": "urban-high-rise", "hookPattern": "warning",
    "storyMeta": {"setting": "half-empty new housing tower", "narrator": "first-person young man", "structure": "three nights + guard's register", "ending": "register reveal, instruction to the viewer"},
    "title": "नौवीं मंज़िल | रात 3:33 की लिफ़्ट | हिंदी हॉरर कहानी",
    "description": "शहर के बाहर एक नई सोसाइटी, आधा ख़ाली टावर, और एक लिफ़्ट जो हर रात 3:33 पर नौवीं मंज़िल पर रुकती है। यह कहानी पूरी तरह काल्पनिक है। इसका किसी असली व्यक्ति, जगह या घटना से कोई संबंध नहीं है।",
    "tags": ["हिंदी हॉरर कहानी", "horror story hindi", "lift horror", "डरावनी कहानी", "fiction"],
    "beats": [
        {"n": "अगर आपकी बिल्डिंग में लिफ़्ट है, तो यह कहानी आख़िर तक सुनिएगा। यह कहानी पूरी तरह काल्पनिक है।\n\nशहर के बाहर एक नई सोसाइटी बनी थी। ऊँचे-ऊँचे टावर, चमकती लॉबी, और किराया इतना कम कि मुझे यक़ीन नहीं हुआ। एजेंट ने बताया, \"टावर सी अभी आधा ख़ाली है, सर। लोग धीरे-धीरे आ रहे हैं।\" मुझे बारहवीं मंज़िल पर फ़्लैट मिला, बारह सौ चार। रात को बालकनी से देखो तो पूरे टावर में गिनती की चार-पाँच खिड़कियाँ जलती थीं। बाक़ी सब अँधेरा।",
         "s": None, "v": atmos("tower_night")},
        {"n": "पहली रात मेरी नींद किसी आवाज़ से खुली। एक हल्की-सी घंटी। डिंग। जैसी लिफ़्ट के दरवाज़े खुलने से पहले बजती है।\n\nमैंने फ़ोन उठाया। रात के तीन बजकर तैंतीस मिनट।\n\nमेरा फ़्लैट लिफ़्ट के बिल्कुल सामने था। मैंने दरवाज़े की आँख से बाहर झाँका। लिफ़्ट के दरवाज़े खुले थे। अंदर पीली रोशनी थी। और अंदर कोई नहीं था। दरवाज़े कुछ देर खुले रहे, जैसे किसी के उतरने का इंतज़ार कर रहे हों। फिर बंद हो गए।",
         "s": None, "v": atmos(seq=[["phone_clock", 0], ["lift_doors_open_empty", 0.45]])},
        {"n": "मैं दरवाज़े से हटने ही वाला था कि मेरी नज़र लिफ़्ट के ऊपर लगी छोटी-सी लाल स्क्रीन पर पड़ी। नंबर बदल रहे थे। बारह। ग्यारह। दस। नौ।\n\nऔर नौ पर आकर नंबर रुक गया।\n\nमैं देर तक उस लाल नौ को देखता रहा। वो हिला नहीं। मुझे नहीं पता मैं कब वापस बिस्तर पर गया, पर उस रात मुझे दोबारा नींद नहीं आई।",
         "s": None, "v": atmos(seq=[["lift_display_down", 0]])},
        {"n": "सुबह नीचे गेट पर बहादुर जी बैठे थे। सोसाइटी के सबसे पुराने गार्ड। उनके केबिन में एक मेज़, एक टेबल लैंप, और एक मोटा-सा रजिस्टर रहता था, जिसमें वो हर आने-जाने वाले का नाम लिखते थे।\n\nमैंने हँसते हुए पूछा, \"बहादुर जी, नौवीं मंज़िल पर कौन रहता है? रात को साढ़े तीन बजे भी लिफ़्ट बुलाते हैं।\"\n\nबहादुर जी का पेन रुक गया। उन्होंने कहा, \"नौवीं मंज़िल पर कोई नहीं रहता, साहब। बिल्डर ने वो पूरी मंज़िल कभी बेची ही नहीं। चारों फ़्लैट बंद हैं।\"\n\nफिर उन्होंने रजिस्टर बंद किया और धीरे से कहा, \"रात को लिफ़्ट मत बुलाया करो। सीढ़ी से आ-जाया करो।\"",
         "s": None, "v": atmos("guard_cabin")},
        {"n": "मैंने उनकी बात हँसी में उड़ा दी। नई बिल्डिंग, नई लिफ़्ट। कोई सेंसर ख़राब होगा, कोई सॉफ़्टवेयर।\n\nदूसरी रात मैंने अलार्म लगाया। तीन बजकर तीस मिनट का। मैं दरवाज़े के पास कुर्सी लगाकर बैठ गया।\n\nतीन बजकर तैंतीस मिनट पर लाल स्क्रीन जली। नौ। फिर दस। ग्यारह। बारह।\n\nडिंग।\n\nदरवाज़े खुले। अंदर कोई नहीं। लेकिन इस बार मैंने कुछ और देखा। लिफ़्ट की पिछली दीवार पर एक बड़ा शीशा लगा था। और उस शीशे पर, अंदर की तरफ़ से, भाप जमी थी। और उस भाप पर किसी ने उँगली से लिखा था। सिर्फ़ एक नंबर।\n\nनौ।",
         "s": None, "v": atmos(seq=[["lift_display_up", 0], ["lift_mirror_fog_nine", 0.55]])},
        {"n": "दरवाज़े बंद होने लगे। और मैंने देखा कि लिफ़्ट के अंदर, बटनों वाले पैनल पर, नौ नंबर का बटन अपने आप जल रहा था।\n\nलिफ़्ट नीचे चली गई। स्क्रीन पर नौ आकर फिर रुक गया।\n\nअगले दिन मैं ऑफ़िस से जल्दी लौट आया। लिफ़्ट में मेरे साथ सातवीं मंज़िल वाली एक आंटी थीं। मैंने यूँ ही पूछा, \"आंटी, आप यहाँ कब से हैं?\" वो बोलीं, \"तीन साल से, बेटा। सबसे पहले हम ही आए थे।\"\n\nफिर उन्होंने मेरी तरफ़ देखा। \"तुम बारह सौ चार में आए हो न? तुमसे पहले वहाँ एक लड़का रहता था। बहुत अच्छा लड़का था। हमेशा सीढ़ी से जाता था। बारह मंज़िल, रोज़। मैंने एक बार पूछा भी था कि लिफ़्ट क्यों नहीं लेते।\"\n\n\"उसने क्या कहा?\"\n\nआंटी ने अपने फ़्लोर का बटन दबाया। \"कहता था, लिफ़्ट में भीड़ बहुत होती है।\"\n\nलिफ़्ट में उस वक़्त सिर्फ़ हम दो लोग थे।",
         "s": None, "v": atmos(seq=[["lift_panel_nine_lit", 0], ["lift_inside_day", 0.35]])},
        {"n": "उस रात मैंने तय किया कि मैं ख़ुद देखूँगा नौवीं मंज़िल पर क्या है। लिफ़्ट से नहीं। सीढ़ी से।\n\nतीन बजकर बीस मिनट पर मैं फ़ोन की टॉर्च जलाकर सीढ़ियाँ उतरने लगा। ग्यारह। दस। सीढ़ियों में अजीब-सी ठंडक थी, जैसे किसी ने एसी चला रखा हो। हर मंज़िल पर एक हरी-सी रोशनी वाला एग्ज़िट बोर्ड जलता था।\n\nनौवीं मंज़िल का एग्ज़िट बोर्ड बुझा हुआ था।",
         "s": None, "v": atmos("abandoned_stairwell_torch")},
        {"n": "मैंने सीढ़ियों का दरवाज़ा धकेला। सामने एक लंबा गलियारा था। दोनों तरफ़ फ़्लैटों के दरवाज़े। नौ सौ एक। नौ सौ दो। नौ सौ तीन। सबके दरवाज़ों पर बिल्डर की प्लास्टिक की पन्नी अब भी चिपकी थी।\n\nगलियारे के आख़िर में नौ सौ चार था।\n\nउसके दरवाज़े के नीचे की दरार से पीली रोशनी आ रही थी।\n\nऔर अंदर से एक आवाज़ आ रही थी। ट्रिंग। ट्रिंग। जैसे इंटरकॉम बज रहा हो।",
         "s": None, "v": atmos("corridor_light_under_door")},
        {"n": "दरवाज़े पर ताला नहीं था। मैंने उसे धीरे से धकेला।\n\nअंदर कुछ नहीं था। न फ़र्नीचर, न पर्दे। सीमेंट का फ़र्श, और उस पर धूल। छत पर एक नंगा बल्ब जल रहा था, जबकि बहादुर जी ने कहा था कि इस मंज़िल का बिजली का मीटर कभी लगा ही नहीं।\n\nदीवार पर एक इंटरकॉम लगा था। उसकी छोटी-सी स्क्रीन पर हरे अक्षरों में लिखा था कि कॉल कहाँ से आ रही है।\n\nबारह सौ चार।\n\nमेरा फ़्लैट। जहाँ इस वक़्त कोई नहीं था।",
         "s": None, "v": atmos(seq=[["empty_dusty_room", 0], ["intercom_1204", 0.55]])},
        {"n": "मुझे नहीं पता मैंने रिसीवर क्यों उठाया। शायद इसलिए कि वो घंटी बंद हो जाए।\n\nदूसरी तरफ़ कोई बोला नहीं। बस साँसें थीं। धीमी, लंबी साँसें। और फिर मुझे समझ आया कि वो साँसें किसकी हैं। मैंने अपनी साँस रोकी। दूसरी तरफ़ की साँस भी रुक गई। मैंने छोड़ी। उधर भी छूटी।\n\nफिर एक आवाज़ आई। धीमी, फुसफुसाती हुई। मेरी अपनी आवाज़।\n\n\"नीचे मत आना।\"",
         "s": None, "v": atmos("intercom_1204")},
        {"n": "मैंने रिसीवर फेंका और गलियारे में भागा। सीढ़ियों का दरवाज़ा अब अंदर से बंद था। मैंने उसे धक्का दिया, खींचा, पर वो हिला नहीं।\n\nपीछे से आवाज़ आई। डिंग।\n\nलिफ़्ट के दरवाज़े खुले थे। अंदर पीली रोशनी थी। और कोई नहीं था।\n\nमेरे पास कोई और रास्ता नहीं था। मैं अंदर घुसा और बारह का बटन ज़ोर से दबाया। दरवाज़े बंद हुए। लिफ़्ट ऊपर चलने लगी।\n\nमैंने सामने वाले शीशे में देखा। उसमें मैं था, हाँफता हुआ, पसीने में भीगा हुआ। और मेरे कंधे के ठीक पीछे, बहुत पास, एक और चेहरा था। उसने अपनी उँगली होंठों पर रखी हुई थी।\n\nश्श्श।",
         "s": None, "v": atmos(seq=[["lift_doors_open_empty", 0], ["lift_mirror_figure_behind", 0.5]])},
        {"n": "मैंने पलटकर नहीं देखा। मैंने आँखें बंद कर लीं और गिनता रहा। दस। ग्यारह। बारह।\n\nडिंग।\n\nदरवाज़े खुले और मैं बाहर गिर पड़ा। अपने फ़्लैट में घुसा, दरवाज़ा बंद किया, और सारी बत्तियाँ जलाकर सुबह तक दीवार से पीठ टिकाकर बैठा रहा।\n\nलिफ़्ट की आवाज़ उस रात फिर नहीं आई।",
         "s": None, "v": atmos(seq=[["black", 0], ["room_plain", 0.5]])},
        {"n": "सुबह मैं सामान बाँधकर नीचे उतरा। सीढ़ी से। बहादुर जी केबिन में थे। मैंने चाबी उनकी मेज़ पर रखी। उन्होंने कुछ नहीं पूछा। बस अपना रजिस्टर मेरी तरफ़ घुमा दिया।\n\nपिछली रात की आख़िरी दो लाइनें उनकी लिखावट में थीं।\n\n\"रात 3:33। लिफ़्ट, बारह से नौ। एक व्यक्ति।\"\n\n\"रात 3:41। लिफ़्ट, नौ से बारह। दो व्यक्ति।\"\n\nमैंने पूछा, \"ये आपने कैसे लिखा? आप तो नीचे थे।\"\n\nबहादुर जी ने लैंप बंद किया। \"मैं हर रात लिखता हूँ, साहब। लिफ़्ट ख़ुद बताती है।\"",
         "s": None, "v": atmos("guard_register")},
        {"n": "उस दिन के बाद मैं कभी अकेले लिफ़्ट में नहीं चढ़ा।\n\nऔर आपसे भी बस इतना कहूँगा। अगर रात को तीन बजकर तैंतीस मिनट पर आपकी मंज़िल पर लिफ़्ट अपने आप आकर रुके, तो उसमें मत चढ़िएगा।\n\nऔर अगर चढ़ ही जाएँ, तो शीशे में मत देखिएगा।",
         "s": None, "v": atmos(seq=[["tower_night", 0], ["black", 0.85]])},
    ],
}

# ---- C2: Epics in English, episode 2 -------------------------------------------
IND = [66, 5, 92, 31]
ROUTE = ["Ayodhya", "Shringverpur", "Prayagraj", "Chitrakoot", "Dandakaranya", "Panchavati", "Lepakshi", "Kishkindha", "Rameswaram"]

def route_geo(upto, new=None, view=IND, lines=None, **kw):
    pts = ROUTE[:upto]
    key = {"Ayodhya", "Chitrakoot", "Panchavati", "Kishkindha", "Rameswaram", new}
    wide = view == IND
    pins = [{"place": n, "label": n if (not wide or n in key) else "", "size": 44, "at": 0 if n != new else 0.15} for n in pts]
    base = [{"places": pts, "at": 0}] if len(pts) > 1 else []
    lines = lines if lines and lines[0].get("places") == ROUTE else base + (lines or [])
    return geo(view=view, fills=[{"name": "India", "label": False, "color": "#1E2740"}, {"name": "Sri Lanka", "label": False, "color": "#1E2740"}],
               pins=pins, lines=lines, **kw)

EPICS = {
    "channel": "d-epics-en",
    "slug": "rama-route-on-a-map",
    "format": "long", "lang": "en",
    "topic": "Rama's exile route from Ayodhya to Lanka, on a map",
    "angle": "Plot the places tradition ties to the exile, and the route crosses most of India",
    "cluster": "ramayana-basics", "hookPattern": "map-reveal",
    "versionFollowed": "Valmiki Ramayana (Ayodhya to Yuddha Kanda); modern locations are traditional identifications, not archaeological findings",
    "title": "Rama's 14-Year Exile on a Map | Ayodhya to Lanka, Explained",
    "description": "Ayodhya, Chitrakoot, Panchavati, Kishkindha, Rameswaram: the places tradition links to Rama's exile, plotted in order. Version followed: Valmiki Ramayana. Modern sites are traditional identifications; Valmiki gives no map coordinates.",
    "tags": ["Ramayana", "Hindu mythology", "Rama", "map", "Ram Setu", "Indian history"],
    "beats": [
        {"n": "Rama walked from Ayodhya to Lanka. Plot the places that tradition links to his exile, and the route crosses most of the Indian subcontinent.",
         "s": "AYODHYA → LANKA", "v": route_geo(9)},
        {"n": "One thing first. Valmiki names these places. He doesn't give map coordinates. The modern sites you'll see are traditional identifications, believed by pilgrims for centuries, not archaeological proof.",
         "s": "TRADITION, NOT GPS", "v": cards([["Valmiki", "Names the places"], ["Tradition", "Links them to modern sites"]]),
         "c": "Valmiki names many of these places but does not give modern map locations.", "u": S["hindutone_trail"]},
        {"n": "It starts in Ayodhya, capital of the kingdom of Kosala. King Dasharatha has three queens and four sons. Rama is the eldest, and the king decides to crown him.",
         "s": "AYODHYA", "v": route_geo(1, view=[78, 22, 88, 30]),
         "c": "Dasharatha, king of Kosala, had three wives; he decided to crown Rama.", "u": S["wiki_exile"]},
        {"n": "But years earlier, Queen Kaikeyi had saved Dasharatha's life in battle, and he promised her two boons. A maid named Manthara convinces her to cash them in.",
         "s": "TWO BOONS", "v": cards(["Boon 1", "Boon 2"]),
         "c": "Kaikeyi received two boons after saving Dasharatha in battle; Manthara persuaded her to use them.", "u": S["wisdomlib_ak18"]},
        {"n": "Boon one: her son Bharata gets the throne. Boon two: Rama goes into exile, in the Dandaka forest, for fourteen years.",
         "s": "14 YEARS", "v": cards([["Boon 1", "Bharata is crowned"], ["Boon 2", "Rama: 14 years in exile"]]),
         "c": "Kaikeyi asked for Bharata's installation and Rama's exile to the Dandaka forest for fourteen years.", "u": S["wisdomlib_ak18"]},
        {"n": "Rama accepts without protest. A king's word must be kept. His wife Sita and his brother Lakshmana refuse to stay behind.",
         "s": None, "v": kinetic("A KING'S WORD"),
         "c": "Rama is exiled with Sita and Lakshmana for 14 years.", "u": S["wiki_exile"]},
        {"n": "Stop two. Shringverpur, on the Ganga. Here the boatman-king Guha ferries them across the river.",
         "s": "SHRINGVERPUR", "v": route_geo(2, new="Shringverpur", view=[78, 22, 88, 30]),
         "c": "Shringverpur on the Ganga is where Guha met Rama.", "u": S["hindutone_trail"]},
        {"n": "Then Prayagraj, where the Ganga and Yamuna meet, and the hermitage of the sage Bharadvaja.",
         "s": "PRAYAGRAJ", "v": route_geo(3, new="Prayagraj", view=[78, 22, 88, 30])},
        {"n": "Stop four. Chitrakoot. Their first real forest home.",
         "s": "CHITRAKOOT", "v": route_geo(4, new="Chitrakoot", view=[76, 20, 88, 30]),
         "c": "Chitrakoot was the first forest home.", "u": S["hindutone_trail"]},
        {"n": "Back in Ayodhya, Dasharatha dies of grief. Bharata, horrified at what his mother has done, walks to Chitrakoot to bring Rama home.",
         "s": None, "v": route_geo(4, view=[76, 20, 88, 30], lines=[{"places": ["Ayodhya", "Chitrakoot"], "color": "#3DD6C6", "at": 0.2}]),
         "c": "After Rama's departure Dasharatha dies of grief; Bharata goes to bring Rama back.", "u": S["wiki_exile"]},
        {"n": "Rama refuses. Fourteen years means fourteen years. So Bharata takes Rama's sandals, places them on the throne, and rules as a caretaker.",
         "s": "THE SANDALS", "v": kinetic("THE SANDALS ON THE THRONE"),
         "c": "Rama refuses to return before the exile ends.", "u": S["sanskritdocs_ak107"]},
        {"n": "Then they go deep south, into Dandakaranya, a vast forest that tradition places across central India, including the Bastar region of today's Chhattisgarh.",
         "s": "DANDAKARANYA", "v": route_geo(5, new="Dandakaranya"),
         "c": "Chhattisgarh's Ram Van Gaman circuit includes Jagdalpur in Bastar.", "u": S["wiki_rvgp"]},
        {"n": "Stop six. Panchavati, on the Godavari, at today's Nashik. The name means five banyan trees. This is where the story turns.",
         "s": "PANCHAVATI", "v": route_geo(6, new="Panchavati"),
         "c": "Panchavati at Nashik on the Godavari; the name means five banyan trees.", "u": S["hindutone_trail"]},
        {"n": "Here, Ravana's sister Surpanakha meets the brothers and is spurned. Lakshmana cuts off her nose, and she flies to Lanka for revenge.",
         "s": "SURPANAKHA", "v": kinetic("SURPANAKHA"),
         "c": "Surpanakha, Ravana's sister, is spurned and mutilated by Lakshmana, setting up the abduction.", "u": S["wiki_ramayana"]},
        {"n": "A golden deer appears. Rama chases it. Lakshmana follows. And Ravana, king of Lanka, carries Sita away.",
         "s": "SITA IS TAKEN", "v": kinetic("THE GOLDEN DEER"),
         "c": "Panchavati is where Sita was carried off.", "u": S["hindutone_trail"]},
        {"n": "The old vulture Jatayu tries to stop him and falls. Tradition places that fight at Lepakshi, in today's Andhra Pradesh.",
         "s": "LEPAKSHI", "v": route_geo(7, new="Lepakshi"),
         "c": "Lepakshi is linked with Jatayu.", "u": S["hindutone_trail"]},
        {"n": "Searching south, the brothers reach Kishkindha, the kingdom of the vanaras. It's usually identified with the area around Hampi, on the Tungabhadra river.",
         "s": "KISHKINDHA · HAMPI", "v": route_geo(8, new="Kishkindha"),
         "c": "Kishkindha is often identified with the region around the Tungabhadra near Hampi.", "u": S["outlook_kishkindha"]},
        {"n": "Earlier, deep in the forest, an old woman named Shabari, who had waited years for Rama, had welcomed them and pointed them toward Sugriva.",
         "s": "SHABARI", "v": kinetic("SHABARI'S WAIT"),
         "c": "Shabari directs Rama to Sugriva.", "u": S["wiki_ramayana"]},
        {"n": "Sugriva is a monkey prince in hiding, driven out by his brother Vali. Rama kills Vali, and Sugriva becomes king. In return, he sends his search parties out in every direction.",
         "s": "SUGRIVA · VALI", "v": cards([["Vali", "The usurping brother"], ["Sugriva", "Rama's ally"]]),
         "c": "Rama kills Vali and restores Sugriva, who sends search parties for Sita.", "u": S["wiki_ramayana"]},
        {"n": "Sugriva's minister Hanuman crosses the sea, finds Sita in Lanka, shows her Rama's ring, and brings back her jewel as proof.",
         "s": "HANUMAN", "v": route_geo(8, view=[70, 4, 88, 22], lines=[{"places": ["Kishkindha", "Sri Lanka"], "color": "#3DD6C6", "at": 0.25}])},
        {"n": "Before he leaves, Hanuman lets himself be captured. His tail is set on fire, and he uses it to burn Lanka.",
         "s": "LANKA BURNS", "v": kinetic("LANKA BURNS"),
         "c": "Hanuman's tail is set on fire and he burns Lanka.", "u": S["wiki_ramayana"]},
        {"n": "Ravana's own brother, Vibhishana, begs him to return Sita. Ravana throws him out, and Vibhishana crosses over to Rama's side.",
         "s": "VIBHISHANA", "v": cards([["Ravana", "Refuses"], ["Vibhishana", "Joins Rama"]]),
         "c": "Vibhishana, Ravana's brother, defects to Rama.", "u": S["wiki_ramayana"]},
        {"n": "The army marches to the coast at Rameswaram, the last stop in India.",
         "s": "RAMESWARAM", "v": route_geo(9, new="Rameswaram", view=[70, 4, 88, 22]),
         "c": "Rameswaram is where the army crossed to Lanka.", "u": S["hindutone_trail"]},
        {"n": "In the epic, the vanaras build a bridge across the sea. Today, between Rameswaram's island and Sri Lanka's Mannar Island, there's a chain of limestone shoals about forty eight kilometres long, called Ram Setu, or Adam's Bridge.",
         "s": "RAM SETU · 48 KM", "v": geo(view=[78.8, 8.6, 80.3, 9.7], pins=[{"place": "Dhanushkodi"}, {"place": "Talaimannar", "label": "Mannar Island"}],
                                          lines=[{"places": ["Dhanushkodi", "Talaimannar"], "at": 0.15}]),
         "c": "Adam's Bridge / Ram Setu is a 48 km chain of limestone shoals between Rameswaram (Pamban) Island and Mannar Island.", "u": S["esa_adams"]},
        {"n": "Geologists describe the shoals as natural, a former land link exposed and drowned as sea levels changed. For millions of devotees, it is Rama's bridge. You can hold both facts at once.",
         "s": None, "v": cards([["Geology", "Natural limestone shoals"], ["Faith", "Rama's Setu"]]),
         "c": "Adam's Bridge is described as natural limestone shoals; geological evidence suggests a former land connection.", "u": S["wiki_adams"]},
        {"n": "The war is fought in Lanka. Ravana falls. Sita is free. And fourteen years after they left, they fly home to Ayodhya.",
         "s": None, "v": route_geo(9, lines=[{"places": ROUTE, "at": 0}, {"coords": [[79.9, 7.5], [82.2, 26.8]], "color": "#3DD6C6", "at": 0.3}])},
        {"n": "Add up only the straight lines between these stops, and it's already about three and a half thousand kilometres. On foot, through forest, it would be far more.",
         "s": "~3,600 KM", "v": number([["km, straight lines between stops", 3583]]),
         "c": "Great-circle sum of Ayodhya→Shringverpur→Prayagraj→Chitrakoot→Jagdalpur→Nashik→Lepakshi→Hampi→Rameswaram ≈ 3,583 km.", "u": S["hindutone_trail"], "computed": True},
        {"n": "Today, governments are turning this into a pilgrimage circuit, the Ram Van Gaman Path. Two hundred and forty eight places in India and Sri Lanka have been identified along it.",
         "s": "248 PLACES", "v": number([["places identified on the route", 248]]),
         "c": "A total of 248 places in India and Sri Lanka have been identified on the Ram Van Gaman Path.", "u": S["wiki_rvgp"]},
        {"n": "So that's the journey. Nine stops, one promise, fourteen years. Which of these places would you visit first? Tell me in the comments.",
         "s": None, "v": route_geo(9)},
    ],
}

# Scene changes anchored to phrases in the narration: word timings are spread
# evenly inside a beat, so a phrase's character offset approximates its time.
CUTS = [
    [("tower_night", None), ("room_plain", "मुझे बारहवीं मंज़िल"), ("tower_night", "रात को बालकनी")],
    [("room_interior_fan", None), ("phone_clock", "मैंने फ़ोन उठाया"), ("lift_doors_open_empty", "मेरा फ़्लैट लिफ़्ट"), ("lift_doors_closed", "फिर बंद हो गए")],
    [("lift_display_down", None), ("room_interior_fan", "मैं देर तक")],
    [("guard_cabin", None), ("tower_night", "नौवीं मंज़िल पर कोई नहीं"), ("guard_cabin", "फिर उन्होंने रजिस्टर")],
    [("room_plain", None), ("phone_clock", "दूसरी रात"), ("lift_display_up", "तीन बजकर तैंतीस मिनट पर लाल"), ("lift_doors_open_empty", "डिंग।\n\nदरवाज़े"), ("lift_mirror_fog_nine", "लेकिन इस बार मैंने")],
    [("lift_panel_nine_lit", None), ("lift_display_down", "लिफ़्ट नीचे चली गई"), ("lift_inside_day", "अगले दिन"), ("black", "लिफ़्ट में उस वक़्त")],
    [("room_plain", None), ("phone_clock", "तीन बजकर बीस"), ("abandoned_stairwell_torch", "सीढ़ियाँ उतरने"), ("black", "नौवीं मंज़िल का एग्ज़िट")],
    [("corridor_light_under_door", None)],
    [("empty_dusty_room", None), ("intercom_1204", "दीवार पर एक इंटरकॉम")],
    [("intercom_1204", None), ("black", "फिर एक आवाज़ आई")],
    [("corridor_light_under_door", None), ("lift_doors_open_empty", "पीछे से आवाज़"), ("lift_display_up", "लिफ़्ट ऊपर चलने"), ("lift_mirror_figure_behind", "मैंने सामने वाले शीशे")],
    [("black", None), ("lift_doors_open_empty", "दरवाज़े खुले"), ("room_plain", "अपने फ़्लैट में घुसा")],
    [("guard_cabin", None), ("guard_register", "पिछली रात की आख़िरी")],
    [("tower_night", None), ("black", "और अगर चढ़ ही")],
]
assert len(CUTS) == len(HORROR["beats"])
for _b, cuts in zip(HORROR["beats"], CUTS):
    t = _b["n"]; seq = []
    for name, phrase in cuts:
        if phrase is None: seq.append([name, 0]); continue
        i = t.find(phrase); assert i >= 0, phrase
        seq.append([name, round(i / len(t), 3)])
    _b["v"] = ("atmos", {"scene": seq[0][0], "sequence": seq, "time": "3:20" if "तीन बजकर बीस" in t else "3:33"})
