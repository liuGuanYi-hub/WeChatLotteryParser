class WeChatLotteryException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class InvalidImageFormat(WeChatLotteryException):
    def __init__(self, message: str = "请上传 PNG、JPG 或 JPEG 格式的图片"):
        super().__init__("INVALID_FORMAT", message, 400)


class ImageTooLarge(WeChatLotteryException):
    def __init__(self, message: str = "图片大小不能超过 10MB"):
        super().__init__("FILE_TOO_LARGE", message, 400)


class NoAvatarDetected(WeChatLotteryException):
    def __init__(self, message: str = "未检测到参与者头像，请上传清晰的截图"):
        super().__init__("NO_AVATAR", message, 404)


class NoNicknameDetected(WeChatLotteryException):
    def __init__(self, message: str = "未识别到昵称，请确保图片清晰"):
        super().__init__("NO_NICKNAME", message, 404)


class OCRError(WeChatLotteryException):
    def __init__(self, message: str = "文字识别失败，请重试"):
        super().__init__("OCR_ERROR", message, 500)


class InsufficientParticipants(WeChatLotteryException):
    def __init__(self, message: str = "参与者数量不足，至少需要 2 人"):
        super().__init__("INSUFFICIENT_PARTICIPANTS", message, 400)


class EmptyParticipants(WeChatLotteryException):
    def __init__(self, message: str = "参与者列表不能为空"):
        super().__init__("EMPTY_PARTICIPANTS", message, 400)


class WinnerNotFound(WeChatLotteryException):
    def __init__(self, message: str = "未找到指定的中奖者"):
        super().__init__("WINNER_NOT_FOUND", message, 404)


class LotteryInProgress(WeChatLotteryException):
    def __init__(self, message: str = "抽奖正在进行中"):
        super().__init__("LOTTERY_IN_PROGRESS", message, 409)