import logging
from collections import OrderedDict
import hlt
import pprint

game = hlt.Game("v20")
logging.info("v20 log")

def get_notfull_n_empty(ship):
    result = {}
    for planet in game_map.all_planets():
        if not planet.is_full() and (planet.owner == mybot or not planet.owner):
            result.setdefault(ship.calculate_distance_between(planet) / planet.radius, []).append(planet)
    result = OrderedDict(sorted(result.items(), key=lambda t: t[0]))
    result2 = [result[distance][0] for distance in result]
    return result2

def get_mybot_planets_by_radius():
    result = []
    for planet in game_map.all_planets():
        if planet.owner == mybot:
            result.setdefault(planet.radius, []).append(planet)
    result = OrderedDict(sorted(result.items(), key=lambda t: t[0]))
    result2 = [result[distance][0] for distance in result]
    return result2

def get_mybot_planets_by_dist(ship):
    result = {}
    for planet in game_map.all_planets():
        if planet.owner == mybot:
            result.setdefault(ship.calculate_distance_between(planet), []).append(planet)
    result = OrderedDict(sorted(result.items(), key=lambda t: t[0]))
    result2 = [result[distance][0] for distance in result]
    return result2

def attack(enemy_ship):
    nav_pos = ship.closest_point_to(enemy_ship)
    flag_a =True
    navigate_command = None
    if timeout:
        obstacles = game_map.obstacles_between(ship, nav_pos)
        if len(obstacles) > 1:
            flag_a = False
    if flag_a:
        navigate_command = ship.navigate(
                nav_pos,
                game_map,
                speed=nav_speed,
                max_corrections = timeout_corrections,
                ignore_ships=False)
    if navigate_command and flag_a:
        command_queue.append(navigate_command)

def sort_closest_enemy_ships(entity):
    enemy_ships = game_map._all_ships()
    result = {}
    for enemy_ship in enemy_ships:
        if  enemy_ship not in mybot.all_ships():
            result.setdefault(entity.calculate_distance_between(enemy_ship), []).append(enemy_ship) 
    result = OrderedDict(sorted(result.items(), key=lambda t: t[0]))
    result2 = [result[distance][0] for distance in result]
    return result2

def all_planets_occupied():
    for planet in game_map.all_planets():
        if not planet.is_full():
            return False
    return True

def get_player_number():
    logging.info("getting player numbers")
    logging.info(len(game.map.all_players()))
    return len(game.map.all_players())

def timeout_ship_count():
    if(len(mybot.all_ships()) > 110):
        return True
    else:
        return False

def get_asas_number():   
    playernumber = get_player_number()
    if playernumber > 2:
        if len(mybot.all_ships()) <3:
            return 0
        result = int(len(mybot.all_ships())/5)
        if result <= 1:
            return 1
        else:
            return 2
    else:
        if len(mybot.all_ships()) <3:
            return 0
        if len(mybot.all_ships()) ==3:
            return 1
        result = len(mybot.all_ships())/4.34
        if result >= 3:
            return 3
        else:
            return 2
        #else:
        #    return int(result)

def get_closest_enemy_planet():
    result = []
    for planet in game_map.all_planets():
        if planet.owner != mybot and not planet.owner:
            result.setdefault(ship.calculate_distance_between(planet), []).append(planet)
    result = OrderedDict(sorted(result.items(), key=lambda t: t[0]))
    result2 = [result[distance][0] for distance in result]
    return result2


def get_closest_damaged_ally_ships_to(entity):
    ally_ships = mybot.all_ships()
    result = {}
    for ally_ship in ally_ships:
        if ship.health < hlt.constants.MAX_SHIP_HEALTH:
            result.setdefault(entity.calculate_distance_between(ally_ship), []).append(ally_ship) 
    result = OrderedDict(sorted(result.items(), key=lambda t: t[0]))
    result2 = [result[distance][0] for distance in result]
    return result2



playernumber = get_player_number()
turn = 1
nav_speed = int(hlt.constants.MAX_SPEED)

while True: #turns
    logging.info(" Turn:" + str(turn))    
    game_map = game.update_map()
    command_queue = []
    mybot = game_map.get_me()
    team_ships = mybot.all_ships()
    timeout = timeout_ship_count()
    as_counter=get_asas_number()
    shipno = 0
    defense_mechanism= False
    timeout_corrections = 100

    for ship in team_ships:
        shipno+=1
        flag = True
        navigate_command = None
        closest_enemy_ships = sort_closest_enemy_ships(ship)
        if timeout:
            if shipno > 85*len(team_ships)/100:
                continue 
            timeout_corrections=int(timeout_corrections*0,97)
            if timeout_corrections < 1:
                timeout_corrections=1     

        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            if ship.health < hlt.constants.MAX_SHIP_HEALTH and ship.health > 0 and ship.calculate_distance_between(closest_enemy_ships[0]) < 5:
                defense_mechanism = True
            continue       

        available_planets =  get_notfull_n_empty(ship)

        target_planet = available_planets[0]
        if timeout and len(available_planets) > 1 and ship.can_dock(target_planet):        
            command_queue.append(ship.dock(target_planet))
            continue
        #if(as_counter>0 and turn < 180/playernumber):
        if(as_counter>0):
            target = closest_enemy_ships[0]
            i = 0
            while target.docking_status == ship.DockingStatus.UNDOCKED:
                i+=1
                if i == len(closest_enemy_ships):
                    target = closest_enemy_ships[0]
                    break
                target = closest_enemy_ships[i]
            if(ship.calculate_distance_between(closest_enemy_ships[0]) < 13 and target.docking_status == ship.DockingStatus.UNDOCKED and playernumber !=2):
               logging.info("running awaaaaaay")
               if len(get_mybot_planets_by_dist(ship)) > 0:
                    target = get_mybot_planets_by_dist(ship)[0]

            nav_pos = ship.closest_point_to(target)

            if timeout:
                obstacles = game_map.obstacles_between(ship, nav_pos)
                if len(obstacles) > 1:
                    flag = False
                    #continue
            if flag:
                navigate_command = ship.navigate(
                        nav_pos,
                        game_map,
                        speed=nav_speed,
                        max_corrections = timeout_corrections,
                        ignore_ships=timeout)

            if navigate_command and flag:
                command_queue.append(navigate_command)
            as_counter -=1
            continue

        if defense_mechanism:
            damaged_allies = get_closest_damaged_ally_ships_to(ship)
            if len(damaged_allies)>0:
                target = damaged_allies[0]
                if ship.calculate_distance_between(damaged_allies[0]) < 10:
                    target = closest_enemy_ships[0]
            else:
                if len(get_mybot_planets_by_dist(ship)) > 0:
                    target = get_mybot_planets_by_dist(ship)[0] 
            nav_pos = ship.closest_point_to(target)
            navigate_command = ship.navigate(
                                        nav_pos,
                                        game_map,
                                        speed=nav_speed,
                                        max_corrections = timeout_corrections,
                                        ignore_ships=timeout)
            if navigate_command:
                command_queue.append(navigate_command)
            continue

        if len(available_planets) > 0 and not (len(available_planets) == 1 and playernumber ==4):       
            target_planet = available_planets[0]   
            if ship.can_dock(target_planet):
                if len(closest_enemy_ships) > 0 and ship.calculate_distance_between(closest_enemy_ships[0]) < 6:
                    attack(closest_enemy_ships[0])
                else:
                    command_queue.append(ship.dock(target_planet))
            else:
                nav_pos = ship.closest_point_to(target_planet)
                if timeout:
                    obstacles = game_map.obstacles_between(ship, nav_pos)
                    if len(obstacles) > 1:
                        continue
                if flag:
                    navigate_command = ship.navigate(
                            nav_pos,
                            game_map,
                            speed=nav_speed,
                            max_corrections = timeout_corrections,
                            ignore_ships=timeout)
                if navigate_command:
                    command_queue.append(navigate_command)
        # FIND SHIP TO ATTACK! lets not do that
        elif len(closest_enemy_ships) > 0:
            attack(closest_enemy_ships[0])
    #end of ships for loop
    game.send_command_queue(command_queue)
    turn+=1
    # TURN END
# GAME END
