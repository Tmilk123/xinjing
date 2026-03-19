from dataclasses import dataclass


@dataclass
class ScoreResult:
    total: int
    max_score: int
    level: str
    color: str
    desc: str


def calculate_score(scale: str, answers: list[int]) -> ScoreResult:
    scale = scale.lower()

    if scale == "sds":
        reverse_indices = {4, 5, 10, 11, 13, 15, 16, 17, 19}
        raw = 0
        for idx, val in enumerate(answers):
            safe_val = val if val is not None else 1
            raw += (5 - safe_val) if idx in reverse_indices else safe_val
        total = int(raw * 1.25)
        if total < 53:
            return ScoreResult(total, 100, "正常", "#22c55e", "无明显抑郁症状，情绪状态良好，请继续保持健康的生活方式。")
        if total <= 62:
            return ScoreResult(total, 100, "轻度抑郁", "#eab308", "存在轻度抑郁倾向，建议关注情绪变化，适当调节压力与作息。")
        if total <= 72:
            return ScoreResult(total, 100, "中度抑郁", "#f97316", "存在中度抑郁症状，建议寻求专业心理咨询和支持。")
        return ScoreResult(total, 100, "重度抑郁", "#dc2626", "存在重度抑郁症状，请尽快寻求专业心理医生的帮助。")

    if scale == "pss":
        reverse_indices = {3, 4, 6, 7}
        total = 0
        for idx, val in enumerate(answers):
            safe_val = val if val is not None else 0
            total += (4 - safe_val) if idx in reverse_indices else safe_val
        if total <= 13:
            return ScoreResult(total, 40, "低压力水平", "#22c55e", "压力处于可控范围内，您的应对能力良好。")
        if total <= 26:
            return ScoreResult(total, 40, "中等压力水平", "#eab308", "存在一定压力，建议采用有效的压力管理和放松策略。")
        return ScoreResult(total, 40, "高压力水平", "#dc2626", "压力水平较高，持续高压可能影响身心健康，建议积极寻求支持。")

    if scale == "ais":
        total = sum(v or 0 for v in answers)
        if total <= 4:
            return ScoreResult(total, 32, "无睡眠障碍", "#22c55e", "睡眠质量良好，无明显障碍。")
        if total <= 10:
            return ScoreResult(total, 32, "可疑失眠", "#eab308", "存在可疑失眠症状，建议关注和改善睡眠卫生习惯。")
        if total <= 14:
            return ScoreResult(total, 32, "轻度失眠", "#f97316", "轻度失眠，建议建立规律的作息时间和睡前放松习惯。")
        if total <= 20:
            return ScoreResult(total, 32, "中度失眠", "#ef4444", "中度失眠，建议寻求专业睡眠咨询或认知行为治疗。")
        return ScoreResult(total, 32, "重度失眠", "#dc2626", "重度失眠，建议尽快就医，排查潜在原因。")

    # default phq9
    total = sum(v or 0 for v in answers)
    if total <= 4:
        return ScoreResult(total, 27, "无抑郁症状", "#22c55e", "您目前状态良好，请继续保持健康的生活方式。")
    if total <= 9:
        return ScoreResult(total, 27, "轻度抑郁", "#eab308", "存在轻度抑郁倾向，建议关注情绪状态，适当自我调适。")
    if total <= 14:
        return ScoreResult(total, 27, "中度抑郁", "#f97316", "存在中度抑郁症状，建议寻求专业心理咨询。")
    if total <= 19:
        return ScoreResult(total, 27, "中重度抑郁", "#ef4444", "存在较重抑郁症状，强烈建议尽快寻求专业帮助。")
    return ScoreResult(total, 27, "重度抑郁", "#dc2626", "存在严重抑郁症状，请立即寻求专业心理医生帮助。")


def build_default_recommendations(scale: str, level: str) -> list[str]:
    common = [
        "保持规律作息，每天保证7小时以上睡眠。",
        "每周进行3次轻度有氧运动，如散步或瑜伽。",
        "使用心镜情绪陪伴功能，进行日常情绪疏导对话。",
    ]
    if scale == "ais":
        common.insert(0, "睡前1小时避免使用手机和电脑，减少蓝光刺激。")
    if "重度" in level:
        common.append("建议尽快寻求线下专业心理医生的帮助。")
    return common
