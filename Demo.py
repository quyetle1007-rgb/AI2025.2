
from MetroGraph import MetroGraph
from Admin import ScenarioManager

mg = MetroGraph(transfer_penalty=4.0)
mg.load_from_json("brussels_metro_dataset (1).json")
manager = ScenarioManager()


def print_stations():
    print("\nDanh sách ga (ID để nhập):")
    for sid, s in sorted(mg.stations.items(), key=lambda x: x[1].name):
        print(f"  {sid:<30} {s.name}")

def print_route(result, mg, label="Kết quả"):
    print(f"\n[{label}]")
    if "error" in result:
        print(f"  Lỗi: {result['error']}")
        return
    path = result["path"]
    # Dùng path_lines từ Dijkstra — path_lines[i] = line đi VÀO ga path[i]
    path_lines = result.get("path_lines", [None] * len(path))
    transfers  = result.get("transfers", 0)

    print(f"  Thời gian  : {result['total_time_min']} phút")
    print(f"  Số ga      : {len(path)}")
    print(f"  Đổi tuyến  : {transfers} lần")
    print("  Lộ trình   :")
    for i, sid in enumerate(path):
        name     = mg.stations[sid].name if sid in mg.stations else sid
        cur_line = path_lines[i] if i < len(path_lines) else None
        prv_line = path_lines[i-1] if i > 0 else None
        line_str = f"[L{cur_line}]" if cur_line else "[--]"
        # Đổi tuyến khi line đến ga này khác line đến ga trước
        transfer_note = f"  << đổi sang Line {cur_line}" if (prv_line and cur_line and cur_line != prv_line) else ""
        print(f"    {line_str}  {name} ({sid}){transfer_note}")

def print_scenarios():
    scs = manager.list_scenarios()
    if not scs:
        print("  (Chưa có scenario nào)")
        return
    for sc in scs:
        status = "ACTIVE" if sc.active else "off"
        print(f"  [{status}] {sc.name}: {sc.description}")
        if sc.closed_stations:
            print(f"        Đóng ga   : {', '.join(sc.closed_stations)}")
        if sc.closed_edges:
            for (u, v, line) in sc.closed_edges:
                line_str = f"line {line}" if line != "*" else "tất cả line"
                print(f"        Đóng cạnh : {u} <-> {v} ({line_str})")
        if sc.delays:
            for (u, v, line), d in sc.delays.items():
                line_str = f"line {line}" if line != "*" else "tất cả line"
                print(f"        Delay     : {u} <-> {v} ({line_str})  +{d} phút")

def ask(prompt):
    return input(f"  {prompt}: ").strip()


#Menu

def menu_scenario():
    while True:
        print("\n--- SCENARIO ---")
        print_scenarios()
        print("""
  1. Tạo scenario mới
  2. Đóng ga
  3. Mở lại ga
  4. Đóng cạnh (đoạn giữa 2 ga)
  5. Mở lại cạnh
  6. Thêm delay
  7. Xóa delay
  8. Bật scenario
  9. Tắt scenario
  10. Xóa scenario
  0. Quay lại""")

        choice = ask("Chọn").strip()

        if choice == "0":
            break

        elif choice == "1":
            name = ask("Tên scenario")
            desc = ask("Mô tả")
            try:
                manager.create_scenario(name, desc)
                print(f"  -> Đã tạo '{name}'")
            except ValueError as e:
                print(f"  Lỗi: {e}")

        elif choice == "2":
            name = ask("Tên scenario")
            sid  = ask("ID ga cần đóng")
            try:
                manager.close_station(name, sid)
                print(f"  -> Đã đóng ga '{sid}' trong '{name}'")
            except ValueError as e:
                print(f"  Lỗi: {e}")

        elif choice == "3":
            name = ask("Tên scenario")
            sid  = ask("ID ga cần mở lại")
            try:
                manager.reopen_station(name, sid)
                print(f"  -> Đã mở lại ga '{sid}'")
            except ValueError as e:
                print(f"  Lỗi: {e}")

        elif choice == "4":
            name = ask("Tên scenario")
            u    = ask("ID ga A")
            v    = ask("ID ga B")
            line = ask("Chỉ đóng line nào? (Enter = tất cả line)")
            try:
                line_arg = line if line else None
                manager.close_edge(name, u, v, line_name=line_arg)
                line_str = f"line {line}" if line else "tất cả line"
                print(f"  -> Đã đóng cạnh {u} <-> {v} ({line_str})")
            except ValueError as e:
                print(f"  Lỗi: {e}")

        elif choice == "5":
            name = ask("Tên scenario")
            u    = ask("ID ga A")
            v    = ask("ID ga B")
            line = ask("Chỉ mở lại line nào? (Enter = tất cả line)")
            try:
                line_arg = line if line else None
                manager.reopen_edge(name, u, v, line_name=line_arg)
                line_str = f"line {line}" if line else "tất cả line"
                print(f"  -> Đã mở lại cạnh {u} <-> {v} ({line_str})")
            except ValueError as e:
                print(f"  Lỗi: {e}")

        elif choice == "6":
            name  = ask("Tên scenario")
            u     = ask("ID ga A")
            v     = ask("ID ga B")
            extra = ask("Thêm bao nhiêu phút")
            line  = ask("Chỉ áp vào line nào? (Enter = tất cả line)")
            try:
                line_arg = line if line else None
                manager.add_delay(name, u, v, float(extra), line_name=line_arg)
                line_str = f"line {line}" if line else "tất cả line"
                print(f"  -> Đã thêm delay +{extra} phút cho {u} <-> {v} ({line_str})")
            except (ValueError, TypeError) as e:
                print(f"  Lỗi: {e}")

        elif choice == "7":
            name = ask("Tên scenario")
            u    = ask("ID ga A")
            v    = ask("ID ga B")
            try:
                manager.remove_delay(name, u, v)
                print(f"  -> Đã xóa delay {u} <-> {v}")
            except ValueError as e:
                print(f"  Lỗi: {e}")

        elif choice == "8":
            name = ask("Tên scenario")
            try:
                manager.activate(name)
                print(f"  -> Đã BẬT '{name}'")
            except ValueError as e:
                print(f"  Lỗi: {e}")

        elif choice == "9":
            name = ask("Tên scenario")
            try:
                manager.deactivate(name)
                print(f"  -> Đã TẮT '{name}'")
            except ValueError as e:
                print(f"  Lỗi: {e}")

        elif choice == "10":
            print("  Nhập tên, hoặc 'ALL' xóa tất cả, 'INACTIVE' xóa các off:")
            inp = ask("Tên")
            try:
                if inp == "ALL":
                    n = manager.delete_all_scenarios()
                    print(f"  -> Đã xóa {n} scenario")
                elif inp == "INACTIVE":
                    deleted = manager.delete_inactive_scenarios()
                    print(f"  -> Đã xóa: {deleted}")
                else:
                    manager.delete_scenario(inp)
                    print(f"  -> Đã xóa '{inp}'")
            except ValueError as e:
                print(f"  Lỗi: {e}")

        else:
            print("  Lựa chọn không hợp lệ.")


#Main

print("\nBRUSSELS METRO")
print_stations()

while True:
    print("\n" + "="*45)

    # Hiện scenario đang active
    active = [sc.name for sc in manager.list_scenarios() if sc.active]
    if active:
        print(f"Scenario đang bật: {', '.join(active)}")
    else:
        print("Scenario: (không có)")

    print("""
  1. Tìm đường đi
  2. Quản lý scenario
  3. Xem danh sách ga
  0. Thoát""")

    choice = ask("Chọn").strip()

    if choice == "0":
        print("PP!")
        break

    elif choice == "1":
        start = ask("Ga xuất phát (ID)")
        end   = ask("Ga đích (ID)")

        # Tuyến gốc
        r_normal = mg.find_shortest_path(start, end)
        print_route(r_normal, mg, "Tuyến gốc (không có scenario)")

        # Tuyến sau scenario
        if active:
            r_sc = manager.find_path(mg, start, end)
            print_route(r_sc, mg, "Tuyến sau khi áp scenario")

            # So sánh thời gian
            if "total_time_min" in r_normal and "total_time_min" in r_sc:
                diff = round(r_sc["total_time_min"] - r_normal["total_time_min"], 2)
                sign = f"+{diff}" if diff >= 0 else str(diff)
                print(f"\n  Chênh lệch: {sign} phút")

    elif choice == "2":
        menu_scenario()

    elif choice == "3":
        print_stations()

    else:
        print("  Lựa chọn không hợp lệ.")
