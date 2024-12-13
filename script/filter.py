import json
import sys


def load_json(file_path):
    """
    从指定路径加载 JSON 数据。
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"加载 JSON 文件时出错: {e}")
        sys.exit(1)


def save_json(data, file_path):
    """
    将数据保存到指定路径的 JSON 文件中。
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"去重后的数据已保存到 {file_path}")
    except Exception as e:
        print(f"保存 JSON 文件时出错: {e}")
        sys.exit(1)


def remove_duplicates(data):
    """
    移除列表中的重复字典对象。
    """
    if not isinstance(data, list):
        print("JSON 数据不是一个列表，无法进行去重操作。")
        sys.exit(1)

    seen = set()
    unique_data = []
    for item in data:
        try:
            item_sorted = {}
            for key, value in item.items():
                if isinstance(value, list):
                    value = tuple(value)
                item_sorted[key] = value
            item_tuple = tuple(sorted(item_sorted.items()))
        except AttributeError:
            print("列表中的元素不是字典类型，无法进行去重操作。")
            sys.exit(1)

        if item_tuple not in seen:
            seen.add(item_tuple)
            unique_data.append(item)

    return unique_data


def remove_duplicates_in_des(data):
    """
    在每个字典对象的 'des' 列表中移除重复项。
    """
    for item in data:
        if "des" in item and isinstance(item["des"], list):
            seen_des = set()
            unique_des = []
            for des_item in item["des"]:
                if des_item not in seen_des:
                    seen_des.add(des_item)
                    unique_des.append(des_item)
            item["des"] = unique_des
    return data


def main():
    input_path = "/Users/tang/Course/Python 程序设计/data_capture/lianjia/bj_rent_house_data.json"
    output_path = "/Users/tang/Course/Python 程序设计/data_capture/lianjia/bj_rent_house_data_clean.json"
    dedup_des = True  # Set to True if you want to deduplicate 'des' lists

    # 加载 JSON 数据
    data = load_json(input_path)
    print(f"去重前的数据量: {len(data)}")

    # 去重
    unique_data = remove_duplicates(data)
    print(f"去重后的数据量: {len(unique_data)}")

    # 可选：在 'des' 列表中去重
    if dedup_des:
        unique_data = remove_duplicates_in_des(unique_data)

    # 保存去重后的数据
    save_json(unique_data, output_path)


if __name__ == "__main__":
    main()
