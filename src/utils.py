from torchvision.transforms import transforms

with open("data/classes.txt", "r", encoding="UTF-8") as file:
    CLASSES = {
        int(target): movie_name
        for class_line in file.readlines()
        for movie_name, target in [class_line.strip().split(": ")]
    }

transform = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)

GREETING = """👋 Привет, киноман! Отправь мне кадр из фильма, и я постараюсь угадать его название! 🎬🔍"""
DONT_KNOW_RESPONSE = """😕 Ой-ой, кажется, я не знаю этот фильм... Попробуй другой кадр, может, повезет! 🎥✨"""
RESPONSE = """🎞️ Хм... Похоже, что это кадр из фильма "{name}"! Но могу и ошибаться. 🤔🎬"""
RESPONSE_LIST = """🤔 Я немного сомневаюсь, но, возможно, этот кадр из одного из этих фильмов:
1️⃣ {top1}
2️⃣ {top2}
3️⃣ {top3}"""

MODEL_NAME = "deit_base_patch16_224"
MODEL_PT_PATH = "data/model.pt"
THRESHOLD_TOP1 = 0.9
THRESHOLD_TOP3 = 0.83
TEMPERATURE = 2.5
