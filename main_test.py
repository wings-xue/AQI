from main import * 

# test now func, rst like 2020-10-08 17:24:00
print(now())


# test save func, 覆盖文本
save(now(), "this is msg")

# test per_hour_aqi_api
for item in per_hour_aqi_api():
    print(item)

# test fetcher
fetcher("http://www.baidu.com")




# test fetcher_nine_index ， 六大区域九个指标测试
# print(fetcher_nine_index("5398"))

# test fetcher 1小时十堰市的空气质量监测结果
for item in per_hour_aqi_api():
    print(fetcher(item, headers))



