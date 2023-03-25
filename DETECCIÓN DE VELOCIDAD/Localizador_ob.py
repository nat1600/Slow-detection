import math

class Localizador_ob(object):
    def __init__(self):
        # Constructor que inicializa la clase
        self.coordenada_centro = {} # Diccionario que guardará el centro de los objetos detectados
        self.conteo_obj = 1 # Variable que se utilizará para asignar un nuevo id a los objetos detectados

    def localizar(self, objetos):
        # Método que localiza los objetos detectados
        objetos_identificados = [] # Lista donde se guardarán los objetos detectados
        for figura in objetos:
            # Iteramos sobre cada figura en la lista de objetos
            x, y, anchoo, alturaa = figura  #x y y son coordenadas que se imparten desde la parte superior izquierda
            punto_centralx = (2*x + anchoo) // 2 # Calculamos el punto central en x
            punto_centraly = (2*y + alturaa) // 2 # Calculamos el punto central en y
            
            # Inicializamos una variable que indicará si se detectó un objeto
            objeto_detectado = False
            
            for id, pt in self.coordenada_centro.items():
                # Iteramos sobre el diccionario que contiene las coordenadas centrales de los objetos detectados
                distancia_obj = math.hypot(punto_centralx - pt[0], punto_centraly - pt[1]) # Calculamos la distancia entre el punto central actual y el punto central en el diccionario

                if distancia_obj < 25:
                    # Si la distancia es menor a 25, actualizamos la coordenada central del objeto y lo agregamos a la lista de objetos detectados
                    self.coordenada_centro[id] = (punto_centralx, punto_centraly)
                    objetos_identificados.append([x, y, anchoo, alturaa, id])
                    objeto_detectado = True
                    break
            
            if objeto_detectado is False:
                # Si no se detecta un objeto con una coordenada central cercana, se agrega un nuevo objeto con una nueva coordenada central al diccionario y se agrega la figura a la lista de objetos detectados con el nuevo id
                self.coordenada_centro[self.conteo_obj] = (punto_centralx, punto_centraly)
                objetos_identificados.append([x, y, anchoo, alturaa, self.conteo_obj])
                self.conteo_obj = self.conteo_obj + 1

        return objetos_identificados
