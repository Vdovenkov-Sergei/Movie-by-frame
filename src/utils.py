from torchvision.transforms import transforms

with open("src/classes.txt", "r", encoding="UTF-8") as file:
    CLASSES = {
        int(target): movie_name
        for class_line in file.readlines()
        for movie_name, target in [class_line.strip().split(":")]
    }

MODEL_NAME = "vit_base_patch16_224"
MODEL_PT_PATH = "src/model.pt"
GREETING = "Привет! Отправь мне кадр из фильма, и я попробую сказать, как называется этот фильм!"
DONT_KNOW_RESPONSE = "Извини, мне кажется, что я не знаю такой фильм. Попробуй отправить мне другой кадр!"
RESPONSE = "Я думаю, что это кадр из фильма {movie_name}, но могу быть не прав. Уверенность: {confidence:.2f}"
THRESHOLD = 0.5

transform = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)
