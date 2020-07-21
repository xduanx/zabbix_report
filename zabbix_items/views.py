import json
import queue
import threading
import time
from io import BytesIO

import psutil
from django.shortcuts import render
from django.template import loader, Context
from django.http import HttpResponse
import os
from zabbix_items import query_data_api

# Create your views here.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def zabbix_report(request):
    all_groups = query_data_api.get_groups()
    all_items = [{"name": "tablespace"}, {"name": "diskgroup"}, {"name": "partition"}, {"name": "cpu"}]
    output_info = []

    if (request.POST.get("action") == "show") and (request.POST.get("groups") is not None) and \
            (request.POST.get("items") is not None):
        group_selected = request.POST.get("groups").split(";")
        items_selected = request.POST.get("items").split(";")
        export_json = {}

        if "diskgroup" in items_selected:
            diskgroup_info_selected = []
            with open(BASE_DIR + "/diskgroup.json", "r") as f:
                diskgroup_all = json.loads(f.read())
                for i in group_selected:
                    for j in diskgroup_all:
                        if j["group"] == i:
                            diskgroup_info_selected.append(j)
                            # diskgroup_all.remove(j)
            export_json.update({"diskgroup": diskgroup_info_selected})
            output_info += diskgroup_info_selected

        if "tablespace" in items_selected:
            tablespace_info_selected = []
            with open(BASE_DIR + "/tablespace.json", "r") as f:
                tablespace_all = json.loads(f.read())
                for i in group_selected:
                    for j in tablespace_all:
                        if j["group"] == i:
                            tablespace_info_selected.append(j)
                            # tablespace_all.remove(j)
            export_json.update({"tablespace": tablespace_info_selected})
            output_info += tablespace_info_selected

        if "partition" in items_selected:
            partition_info_selected = []
            with open(BASE_DIR + "/partition.json", "r") as f:
                partition_all = json.loads(f.read())
                for i in group_selected:
                    for j in partition_all:
                        if j["group"] == i:
                            partition_info_selected.append(j)
                            # partition_all.remove(j)
            export_json.update({"partition": partition_info_selected})
            output_info += partition_info_selected

        if "cpu" in items_selected:
            cpu_info_selected = []
            with open(BASE_DIR + "/cpu.json", "r") as f:
                cpu_all = json.loads(f.read())
                for i in group_selected:
                    for j in cpu_all:
                        if j["group"] == i:
                            cpu_info_selected.append(j)
            export_json.update({"cpu": cpu_info_selected})
            output_info += cpu_info_selected

        with open(BASE_DIR + "/export.json", "w") as f:
            f.write(json.dumps(export_json, indent=4, ensure_ascii=False))
        return HttpResponse(json.dumps(str(output_info)), content_type="application/json,charset=utf-8")

    if request.GET.get("action") == "query":
        query_data_api_process_info = {"start_time": "0", "pid": "0"}
        if os.path.exists(BASE_DIR + "/query_data_api_process_info.txt"):
            with open(BASE_DIR + "/query_data_api_process_info.txt", "r") as f1:
                query_data_api_process_info = json.loads(f1.read())
            try:
                psutil.Process(query_data_api_process_info["pid"])
            except Exception as e:
                query_data_api_process_info = {"start_time": "0", "pid": "0"}
                os.remove(BASE_DIR + "/query_data_api_process_info.txt")
        return HttpResponse(json.dumps(str(query_data_api_process_info)),
                            content_type="application/json,charset=utf-8")
    if request.GET.get("action") == "fetch":
        os.system("python3 " + BASE_DIR + "/zabbix_items/query_data_api.py &")

    if request.GET.get("action") == "export_excel":
        output = BytesIO()
        with open(BASE_DIR + "/report.json", "r") as f:
            report_json = json.loads(f.read())
        query_data_api.write_excel(output, report_json)
        output.seek(0)
        response = HttpResponse(output.getvalue(), content_type='application/vnd.ms-excel')
        file_name = "zabbix_report_" + str(time.strftime('%Y%m%d')) + ".xlsx"
        response['Content-Disposition'] = 'attachment; filename=%s' % file_name
        return response
    data_fetch_time = time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.localtime(os.path.getmtime(BASE_DIR + "/tablespace.json")))
    return render(request, "zabbix_report.html", {"all_groups": all_groups, "all_items": all_items,
                                                  "data_fetch_time": data_fetch_time})


def web_scenaris(request):
    web_scenario_all = query_data_api.get_web_scenario()
    reachable = "1"
    code200 = "1"
    for i in web_scenario_all:
        i.update({"reachable": reachable, "code200": code200})
    for i in query_data_api.get_trigger("14782"):
        if i["value"] == "1":
            if "unreachable" in i["description"]:
                reachable = "0"
            if "Response" in i["description"]:
                code200 = "0"
            for j in web_scenario_all:
                if j["steps"][0]["url"] == i["description"].split()[1]:
                    j["reachable"] = reachable
                    j["code200"] = code200
                    break
    if request.GET.get("query") == "nginx":
        nginx_list = []
        if os.path.exists(BASE_DIR + "/nginx_sort.json"):
            with open(BASE_DIR + "/nginx_sort.json", "r") as nginx_sort:
                url_group = json.loads(nginx_sort.read())
                for k, v in url_group.items():
                    nginx_list.append(list(v))
        else:
            with open(BASE_DIR + "/nginx_sort.json", "w") as nginx_sort:
                nginx_sort.write(json.dumps(query_data_api.nginx_sort()))
                with open(BASE_DIR + "/nginx_sort.json", "r") as nginx_sort:
                    url_group = json.loads(nginx_sort.read())
                    for k, v in url_group.items():
                        nginx_list.append(list(v))
        return HttpResponse(json.dumps(str(nginx_list)), content_type="application/json,charset=utf-8")

    if request.GET.get("query") == "hosts_problem_show":
        nginx_list = []
        hosts_problem_nginx = []
        if not os.path.exists(BASE_DIR + "/nginx_sort.json"):
            with open(BASE_DIR + "/nginx_sort.json", "w") as nginx_sort:
                nginx_sort.write(json.dumps(query_data_api.nginx_sort()))
        with open(BASE_DIR + "/nginx_sort.json", "r") as nginx_sort:
            url_group = json.loads(nginx_sort.read())
            for k, v in url_group.items():
                nginx_list.append(list(v))

        '''
        for x in nginx_list:
            for y in query_data_api.get_problems_backend_ip(x[0]):
                if not y["ip"] in [i["host"] for i in hosts_problem_nginx]:
                    hosts_problem_nginx.append(
                        {"host": y["ip"], "fall_counts": y["fall_counts"], "nginx": x[0], "ignore": "0"})
        '''
        threads = []
        work_queue = queue.Queue(len(nginx_list))
        queue_lock = threading.Lock()
        for x in nginx_list:
            work_queue.put(x[0])

        def get_host_down(nginx_url_queue, host_list):
            while not nginx_url_queue.empty():
                nginx_url = nginx_url_queue.get()
                for p in query_data_api.get_problems_backend_ip(nginx_url):
                    if not p["ip"] in [i["host"] for i in host_list]:
                        host_list.append(
                            {"host": p["ip"], "fall_counts": p["fall_counts"], "nginx": nginx_url, "ignore": "0"})

        for x in range(11):
            t = threading.Thread(target=get_host_down, args=(work_queue, hosts_problem_nginx,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

        with open(BASE_DIR + "/host_problem_nginx_ignore.txt", "r") as hosts_problem_nginx_ignore:
            for x in hosts_problem_nginx_ignore:
                for y in hosts_problem_nginx:
                    if y["host"] == x.rstrip("\n"):
                        y["ignore"] = "1"
        return HttpResponse(json.dumps(str(hosts_problem_nginx)), content_type="application/json,charset=utf-8")

    if request.GET.get("host_problem_ignore"):
        host_problem_ignore = request.GET.get("host_problem_ignore")
        with open(BASE_DIR + "/host_problem_nginx_ignore.txt", "a") as hosts_problem_nginx_ignore:
            hosts_problem_nginx_ignore.write(host_problem_ignore + "\n")
    if request.GET.get("host_problem_restore"):
        host_problem_restore = request.GET.get("host_problem_restore")
        os.system("sed -i \'/^" + host_problem_restore + "/d\' " + BASE_DIR + "/host_problem_nginx_ignore.txt")

    if request.GET.get("query") == "nginx_export":
        output = BytesIO()
        with open(BASE_DIR + "/nginx_sort.json", "r") as f:
            nginx_sort_json = json.loads(f.read())
        query_data_api.nginx_sort_export_excel(output, nginx_sort_json)
        output.seek(0)
        response = HttpResponse(output.getvalue(), content_type='application/vnd.ms-excel')
        file_name = "nginx_list_" + str(time.strftime('%Y%m%d')) + ".xlsx"
        response['Content-Disposition'] = 'attachment; filename=%s' % file_name
        return response
    return render(request, "web_scenaris.html", {"web_scenario_all": web_scenario_all})
