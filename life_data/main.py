import json


TRAITS_SET = {"智商", "健康", "相貌", "毅力", "财富", "幸福"}


def get_trait_value(trait):
    if trait == "智商":
        return "INT"
    elif trait == "健康":
        return "STR"
    elif trait == "相貌":
        return "CHR"
    elif trait == "毅力":
        return "CON"
    elif trait == "财富":
        return "MNY"
    elif trait == "幸福":
        return "HAP"
    else:
        return None


def calculate(s):
    res = ""
    temp = ""
    event_list = []
    n = len(s)
    i = 0
    while i < n:
        # print(temp)
        if s[i] == '｜':
            if len(temp) >= 5:
                event_list.append(temp)
                temp = ""
            # res += "|"
            i += 1
        elif s[i] == '&':
            # if len(temp) >= 5:
            #     event_list.append(temp)
            #     temp = ""
            res += "&"
            i += 1
        elif s[i] == '(':
            res += "("
            i += 1
        elif s[i] == ')':
            if len(temp) >= 5:
                event_list.append(temp)
                temp = ""
            if len(event_list) > 0:
                res += "EVT?[" + ','.join(event_list) + "])"
                event_list = []
            else:
                temp += ")"
            i += 1
        elif s[i] in ('>', '<'):
            if len(event_list) > 0:
                res += "EVT?[" + ','.join(event_list) + "]"
                event_list = []
            if get_trait_value(temp):
                res += get_trait_value(temp) + s[i]
            temp = ""
            i += 1
        else:
            temp += s[i]
            i += 1
    if len(temp) >= 5:
        event_list.append(temp)
        temp = ""
        res += "EVT?[" + ','.join(event_list) + "]"
    res += temp
    # print(res)
    return res


class Age:
    def __init__(self, _id, events, selects):
        self._id = _id
        self.event = events
        self.select = selects


class Event:
    def __init__(self, _id, event=None, is_rand=None, include=None, exclude=None, effect=None,
                 post_event=None, achieve=None):
        self._id = _id
        self.event = None
        self.is_rand = None
        self.include = None
        self.exclude = None
        self.effect = None
        self.postEvent = None
        self.achieve = None

        if event and effect:
            effect = effect.replace(" ", "").replace("，", ",").replace("｜", ",")
            effects = effect.split(',')
            effect_map = {}
            for eff in effects:
                prop = get_trait_value(eff[:2])
                sign = 1 if eff[2] == "+" else -1
                num = int(eff[3:])
                effect_map[prop] = sign * num
            self.effect = effect_map

        if include:
            include = include.replace(" ", "")
            self.include = calculate(include)

        if exclude:
            exclude = exclude.replace(" ", "")
            self.exclude = calculate(exclude)

    def __str__(self):
        return f"Event ID: {self._id}, Name: {self.event}, \
        Is Rand: {self.is_rand}, Include: {self.include}, Exclude: {self.exclude}, Effect: {self.effect}, \
        Post Event: {self.postEvent}, Achieve: {self.achieve}"


class Select:
    def __init__(self, _id, question=None, selections=None, include=None, exclude=None, effects=None):
        self._id = _id
        self.question = None
        self.selections = None
        self.include = None
        self.exclude = None
        self.effects = None

        if question:
            self.question = question.replace(" ", "").replace("[选择]", "")

        if selections:
            selections = selections.replace(" ", "").replace("|", "｜")
            select_list = selections.split('｜')
            self.selections = select_list
            # self.selections = '["' + '","'.join(select_list) + '"]'

        if include:
            include = include.replace(" ", "")
            self.include = calculate(include)

        if exclude:
            exclude = exclude.replace(" ", "")
            self.exclude = calculate(exclude)

    def __str__(self):
        return f"Select ID: {self._id}, Question: {self.question}, Selections: {self.selections}, \
        Include: {self.include}, Exclude: {self.exclude}, Effects: {self.effects}"


def get_age_events_map(file):
    # 打开文件
    with open(file, 'r', encoding='utf-8') as f:
        # 读取表头并丢弃
        f.readline()
        # 初始化空集合
        age_events_map = {}
        # 逐行读取文件内容
        for line in f:
            # 分割行内容，获取第一列的值
            values = line.strip().split('\t')
            age = values[0]
            events = values[1:]
            # 将第一列的值添加到集合中
            if age not in age_events_map:
                age_events_map[age] = []
            age_events_map[age] += events

    # 输出集合
    return age_events_map


def get_selects_set(file):
    # 打开文件
    with open(file, 'r', encoding='utf-8') as f:
        # 读取表头并丢弃
        f.readline()
        # 初始化空集合
        first_column_set = set()
        # 逐行读取文件内容
        for line in f:
            # 分割行内容，获取第一列的值
            values = line.strip().split('\t')
            if len(values) > 1:
                first_column_value = values[1]
                # 将第一列的值添加到集合中
                if "[选择]" in first_column_value:
                    first_column_set.add(values[0])

    # 输出集合
    return first_column_set


def get_age_list(age_events_map, selects_set):
    age_list = []
    for age in age_events_map.keys():
        events = []
        selects = []
        for events_item in age_events_map[age]:
            values = events_item.split('*')
            if values[0] in selects_set:
                selects.append(events_item)
            else:
                events.append(events_item)
        age_list.append(Age(age, events, selects))
    return age_list


def parse_events(file):
    # 打开文件
    with open(file, 'r', encoding='utf-8') as f:
        # 读取表头并丢弃
        f.readline()
        # event list
        event_list = []
        # 逐行读取文件内容
        for line in f:
            # 分割行内容，获取第一列的值
            values = line.strip().split('\t')
            if len(values) < 2:
                continue
            _id = int(values[0])
            event = None
            is_rand = None
            include = None
            exclude = None
            effect = None
            post_event = None
            achieve = None
            if len(values) > 1:
                if "[选择]" in values[1]:
                    continue
                else:
                    event = values[1]
            if len(values) > 3:
                is_rand = values[3]
            if len(values) > 4:
                include = values[4]
            if len(values) > 5:
                exclude = values[5]
            if len(values) > 6:
                effect = values[6]
            if len(values) > 7:
                post_event = values[7]
            if len(values) > 9:
                achieve = values[9]
            event_list.append(Event(_id, event, is_rand, include, exclude, effect, post_event, achieve))
            # print(Event(_id, event, is_rand, include, exclude, effect, post_event, achieve))

    # 输出集合
    return event_list


def parse_selects(file):
    # 打开文件
    with open(file, 'r', encoding='utf-8') as f:
        # 读取表头并丢弃
        f.readline()
        # select list
        select_list = []
        # 逐行读取文件内容
        for line in f:
            # 分割行内容，获取第一列的值
            values = line.strip().split('\t')
            if len(values) < 2:
                continue
            _id = int(values[0])
            include = None
            exclude = None
            effect = None
            if len(values) > 2:
                if "[选择]" not in values[1]:
                    continue
                else:
                    question = values[1]
                    selections = values[2]
                if len(values) > 4:
                    include = values[4]
                if len(values) > 5:
                    exclude = values[5]
                if len(values) > 6:
                    effect = values[6]
                select_list.append(Select(_id, question, selections, include, exclude, effect))
                # print(Select(_id, question, selections, include, exclude, effect))

    # 输出集合
    return select_list


def remove_none(obj):
    return {k: v for k, v in obj.__dict__.items() if v is not None}


def dump_json_file(data_list, file):
    with open(file, "w", encoding='utf-8') as f:
        json.dump([dict(filter(lambda x: x[1] is not None, data.__dict__.items())) for data in data_list],
                  f, ensure_ascii=False)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    age_events_map = get_age_events_map('./age')
    selects_set = get_selects_set('./event')
    dump_json_file(get_age_list(age_events_map, selects_set), "./ages.json")
    dump_json_file(parse_events('./event'), "./event.json")
    dump_json_file(parse_selects('./event'), "./select.json")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
