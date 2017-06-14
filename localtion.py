#!/usr/bin/env python3
#coding:utf-8

import requests
import json

key = '123456'

def get_info(keywords):
    if '中大' in keywords:
        keywords.replace('中大','中山大学')
    elif '中山大学' not in keywords:
        keywords = '中山大学' + keywords
    url = 'http://restapi.amap.com/v3/place/text?&keywords={keywords}&output=JSON&offset=20&page=1&key={key}&extensions=all'.format(keywords=keywords, key=key)
    return json.loads(requests.get(url).content.decode('utf-8'))

def get_address(keywords):
    info = get_info(keywords)
    if info['status'] == '0':
        return info['info']
    else:
        return info['pois'][0]['pname'] + info['pois'][0]['cityname'] + info['pois'][0]['adname'] + (info['pois'][0]['address'] if info['pois'][0]['address'] else '') + info['pois'][0]['name']

def search_around(keywords, radius=500,types=None):
    info = get_info(keywords)
    if info['status'] == '0':
        return info['info']
    location = info['pois'][0]['location']
    address = (info['pois'][0]['address'] if info['pois'][0]['address'] else '') + info['pois'][0]['name']
    if types is None:
        url = 'http://restapi.amap.com/v3/place/around?key={key}&location={location}&output=json&sortrule=distance$offset=4&radius={radius}'.format(key=key, location=location, radius=radius)
    else:
        url = 'http://restapi.amap.com/v3/place/around?key={key}&location={location}&output=json&sortrule=distance&offset=4&radius={radius}&types={types}'.format(key=key, location=location, radius=radius, types=types)

    info = json.loads(requests.get(url).content.decode('utf-8'))
    if info['status'] == '0':
        return info['info']
    else:
        around = [ (x['address'] if x['address'] else '') + x['name'] for x in info['pois'] if x['distance'] != '0']
        around = around[:3]
        around_str = '{address}的附近有：{around}'.format(address=address, around=','.join(around))
        return around_str

def get_direction(origin, destination, how='walking'):
    origin_info = get_info(origin)
    if origin_info['status'] == '0':
        return origin_info['info']
    destination_info = get_info(destination)
    if destination_info['status'] == '0':
        return destination_info['info']        
    origin_location = origin_info['pois'][0]['location']
    destination_location = destination_info['pois'][0]['location']
    city = origin_info['pois'][0]['cityname']
    if 'walk' in how or 'foot' in how:
        how = 'walking'
    elif 'driv' in how or 'car' in how or 'drove' in how:
        how = 'driving'
    elif 'bus' in how:
        how = 'transit/integrated'
    else:
        how = 'walking'
    url = 'http://restapi.amap.com/v3/direction/{how}?origin={origin_location}&destination={destination_location}&output=json&city={city}&key={key}'.format(key=key, how=how, origin_location=origin_location, destination_location=destination_location, city=city)
    info = json.loads(requests.get(url).content.decode('utf-8'))
    if info['status'] == '0':
        return info['info']
    else:
        if how != 'transit/integrated':
            direction = '从{origin}到{destination}的距离为{distance}米，预计{duration}分'.format(origin=origin, destination=destination, distance=info['route']['paths'][0]['distance'], duration=str((int(info['route']['paths'][0]['duration']) + 30) // 60))
        else:
            direction = '从{origin}到{destination}的距离为{distance}米，预计{duration}分'.format(origin=origin, destination=destination, distance=info['route']['distance'], duration=str((int(info['route']['transits'][0]['duration']) + 30) // 60))
        if how == 'walking':
            paths = info['route']['paths']
            steps = paths[0]['steps']    
            direction += '，路线为:\n'
            direction += ',\n'.join([step['instruction'] for step in steps])
        elif how == 'driving':
            paths = info['route']['paths']
            steps = paths[0]['steps']    
            direction += '，路线为:\n'
            direction += ',\n'.join([step['instruction'] for step in steps])
        elif how == 'transit/integrated':
            taxi_cost = info['route']['taxi_cost']
            transits = info['route']['transits']
            cost = transits[0]['cost']
            walking_distance = transits[0]['walking_distance']
            segments = transits[0]['segments']
            direction += ',出租车费用为{taxi_cost}，公交车费用为{cost}，需要步行{walking_distance}米，公交路线为:\n'.format(taxi_cost=taxi_cost, cost=cost, walking_distance=walking_distance)
            steps = []
            for segment in segments:
                try:
                    steps.append('乘坐{name}从{departure_stop}到{arrival_stop}'.format(name=segment['bus']['buslines'][0]['name'], arrival_stop=segment['bus']['buslines'][0]['arrival_stop']['name'], departure_stop=segment['bus']['buslines'][0]['departure_stop']['name']))
                except:
                    for step in segment['walking']['steps']:
                        steps.append(step['instruction'])
            direction += ',\n'.join(steps)
        return direction


