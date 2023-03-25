from tkinter import *
from tkinter import filedialog
import cv2
import numpy as np
import time
import pyscreenshot
from Localizador_ob import *
import Graph as gp


class Grafico_muestra:
    
    # Constructor de la clase Grafico_muestra
    def __init__(self, idvideo, idusuario, idvias, multa):
        # Inicializar las variables de la clase con los argumentos
        self.idVideo = idvideo
        self.idUsuario = idusuario
        self.idVias = idvias
        self.multa = multa

        # Crear una ventana de Tkinter
        ventana = Tk()

        # Crear un botón para abrir el video
        Button(ventana, text="Abrir video a detectar", command=self.abrirVideo).pack()

        # Iniciar el loop principal de la ventana
        ventana.mainloop()


    def abrirVideo(self):
        # Create an instance of the Localizador_ob class
        seguimiento = Localizador_ob()
        # Create an instance of the Graph class
        self.grafic = gp.Graph(self.idVideo, self.idUsuario, self.idVias, self.multa)

        # Open a dialog window to select a video file
        video = filedialog.askopenfilename(title="ABRIR VIDEO PARA DETECCIÓN")
        print(video)
        # Load the video from the selected file
        lecturaVideo = cv2.VideoCapture(video)

        # Create a background subtractor object
        deteccion = cv2.createBackgroundSubtractorMOG2(history=10000, varThreshold=15)

        # Initialize variables
        carI = {}
        car0 = {}
        velocidades = {}
        aux = 0

        # Loop over the video frames
        while (lecturaVideo.isOpened()):
            # Read a frame
            ret, vi = lecturaVideo.read()

            # Get the dimensions of the frame
            alto2 = vi.shape[0]
            ancho2 = vi.shape[1]

            # Create a mask with the shape of the frame
            mascara2 = np.zeros((alto2, ancho2), dtype=np.uint8)

            # Define a polygonal region of interest
            puntos = np.array([[[746, 293], [980, 293], [1142, 792], [476, 792]]])
            cv2.fillPoly(mascara2, puntos, 255)

            # Apply the mask to the frame
            zona = cv2.bitwise_and(vi, vi, mask=mascara2)

            # Define some regions of interest
            area_grande = [(746, 293), (980, 293), (1142, 792), (476, 792)]
            area_1 = [(1142, 792), (476, 792), (590, 590), (1070, 590)]
            area_2 = [(1070, 590), (590, 590), (675, 430), (1022, 430)]
            area_3 = [(746, 293), (980, 293), (1022, 430), (675, 430)]

            # Draw the regions of interest on the frame
            cv2.polylines(vi, [np.array(area_grande, np.int32)], True, (255, 255, 255), 2)
            cv2.polylines(vi, [np.array(area_3, np.int32)], True, (255, 255, 255), 2)
            cv2.polylines(vi, [np.array(area_2, np.int32)], True, (255, 255, 255), 2)
            cv2.polylines(vi, [np.array(area_1, np.int32)], True, (255, 255, 255), 2)

            # Apply some filters to the frame
            mascara = deteccion.apply(zona)
            filtro = cv2.GaussianBlur(mascara, (19, 19),0)
            
            
            
           
            # este es el mas importante porque nos bota las cosas a blanco y negro(umbralizacin binaria)
            _, umbral = cv2.threshold(filtro, 127, 255, cv2.THRESH_BINARY)
            # Aplicar dilatación y cierre para unir regiones cercanas
            dilatacion = cv2.dilate(umbral, np.ones((5, 5)))
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))  # matrices de ceros y unos, convoluciones
            cerrar = cv2.morphologyEx(dilatacion, cv2.MORPH_CLOSE, kernel)

            # se esta aplicando a la zona de interes, es decir mps esta enviando la imagen negra
            # Encontrar los contornos de los objetos detectados
            contornos, _ = cv2.findContours(cerrar, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            detecciones = []

            # Iterar sobre los contornos para encontrar objetos de interés
            for i_contorno in contornos:
                area_objeto = cv2.contourArea(i_contorno)
                if area_objeto > 3000:  # se refiere a pixeles, esta sigue limpiando la imagen, hay puntitos blancos diminutos
                    x, y, ancho, alto = cv2.boundingRect(i_contorno)
                    # cv2.rectangle(zona, (x, y), (x + ancho, y + alto), (255, 255, 0), 3)
                    detecciones.append([x, y, ancho, alto])


            # Se llama al método "localizar" del objeto "seguimiento" y se le pasa como argumento el resultado de la detección
            informacion_objeto_detectado = seguimiento.localizar(detecciones)
            for i_informacion in informacion_objeto_detectado:
                # Se extraen las coordenadas, dimensiones e ID del objeto
                x, y, ancho, alto, id = i_informacion
                
                ## Se calcula la velocidad del objeto y se determina si es un infractor
                vel = 0
                infractor = True
                # Si la velocidad es cero, se asigna un color al objeto
                if vel == 0:
                    color = 0, 255, 255
                # Se dibuja un rectángulo alrededor del objeto en la imagen del video
                cv2.rectangle(vi, (x, y), (x + ancho, y + alto), (color), 2)
                # Se calculan las coordenadas del punto central del objeto
                punto_centralx = int(x + ancho / 2)
                punto_centraly = int(y + alto / 2)

                # Se determina si el objeto se encuentra en la sección 2 de la carretera
                seccion2 = cv2.pointPolygonTest(np.array(area_2, np.int32), (punto_centralx, punto_centraly), False)

                if seccion2 >= 0:
                    carI[id] = time.process_time()
                # Si el objeto ha sido detectado en la sección 2 de la carretera, se registra su tiempo de entrada

                if id in carI:
                    # Se dibuja un círculo en la posición del objeto
                    cv2.circle(vi, (punto_centralx, punto_centraly), 3, (0, 0, 255), -1)
                    # Se determina si el objeto se encuentra en la sección 3 de la carretera
                    seccion3 = cv2.pointPolygonTest(np.array(area_3, np.int32), (punto_centralx, punto_centraly), False)
                    # Si el objeto ha sido detectado en la sección 3 de la carretera, se calcula su velocidad y se determina si es un infractor
                    if seccion3 >= 0:
                        # Si el tiempo es un número entero, se le agrega una fracción de segundo
                        tiempo = time.process_time() - carI[id]
                        if tiempo % 1 == 0:
                            tiempo = tiempo + 0.3234
                            # print(tiempo)
                        # Si el tiempo no es un número entero, se le agrega un segundo
                        if tiempo % 1 != 0:
                            tiempo = tiempo + 1.016
                            # print(tiempo)
                        # Si el ID del objeto no está registrado en el diccionario "car0", se registra su tiempo de paso por la sección 3
                        if id not in car0:
                            car0[id] = tiempo
                        # Si el ID del objeto está registrado en el diccionario "car0", se calcula su velocidad y se determina si es un infractor
                        if id in car0:
                            tiempo = car0[id]
                            vel = 24.5 / car0[id]
                            vel *= 3.6
                            if vel > 60:
                                captura_pantalla = True
                                color = 0, 0, 255


                            else:
                                infractor = False
                                color = 0, 255, 0
                            cv2.rectangle(vi, (x, y), (x + ancho, y + alto), (color), 2)


                        if id in velocidades:
                             # si ya hay una velocidad registrada para este vehículo
                            if velocidades[id][3] == 0:
                                # si aún no se ha registrado la infracción para este vehículo
                                imagen = pyscreenshot.grab()
                                imagen.save(f"Infractor_{str(id)}.png")
                                velocidades[id][3] = f"Infractor_{str(id)}.png"
                                # se guarda la imagen de la infracción y se actualiza la información en el diccionario velocidades

                                #Datos en gráfica
                                self.grafic.guardarCarros(grafica) # se actualiza la información en la gráfica

                        else:
                            # si no hay una velocidad registrada para este vehículo
                            grafica = [id, vel, infractor, 0] # se crea una lista con la información del vehículo
                            velocidades[id] = grafica # se agrega la información del vehículo al diccionario velocidades

                        cv2.rectangle(vi, (x, y - 10), (x + 100, y - 50), (0, 0, 0), -1) # se dibuja un rectángulo negro para el texto de la velocidad
                        cv2.putText(vi, str(int(vel)) + " KM / H", (x, y - 35), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 255), 2) # se escribe la velocidad encima del rectángulo negro
                    cv2.putText(vi, str(id), (x, y - 15), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 2) # se escribe el id del vehículo encima del rectángulo blanco

                cv2.imshow("calle", vi) # se muestra la imagen con los vehículos detectados
                if cv2.waitKey(1) & 0xFF == 27: # si se presiona la tecla Esc, se sale del ciclo while
                    break

                lecturaVideo.release() # se libera la lectura del video
                cv2.destroyAllWindows() # se cierran todas las ventanas de OpenCV

            def envento_boton(self):
                self.grafic.graficarYMostrar() # se muestra la gráfica
                self.grafic = gp.Graph(self.grafic) # se crea una nueva gráfica


