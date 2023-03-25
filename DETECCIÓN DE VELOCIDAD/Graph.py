import random
from tkinter import *
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)


class Graph:

    def __init__(self, *args):
        # Toma argumentos que puede ser la base de datos con el idvideo, idvia y la multa
        # o un objeto de tipo grafica anterior para seguir graficando con datos anteriores
        if (len(args) == 1):
            self.ongoingConstructor(args)
        else:
            self.mainConstructor(args)

    def mainConstructor(self, args):
        # Si no hay argumentos crea todo desde cero
        self.idvideo = args[0]
        self.idusuario = args[1]
        self.idvia = args[2]
        self.multa = args[3]

        self.ventana = Tk()
        self.ventana.resizable(False, False)
        self.ventana.title("SLOW - Graficas y Datos")
        #self.ventana.iconbitmap("RecursosGraficos\\Logo_Slow_Icon_Map.ico")

        self.ancho = 1120
        self.alto = 630

        self.ventana.geometry("{0}x{1}".format(self.ancho, self.alto))
        self.DURACION = 100
        self.carros = []  # Aquí se guarda el carro mientras se da la instrucción de graficar

        self.construirFrames()

    def ongoingConstructor(self, args):
        # Si hay argumentos agrega los vehículos ya creados y establece el tamaño de ventana facilmente
        self.idvideo = args[0].idvideo
        self.idusuario = args[0].idusuario
        self.idvia = args[0].idvia
        self.multa = args[0].multa

        self.ventana = Tk()
        self.ventana.resizable(False, False)
        self.ventana.title("SLOW - Graficas y Datos")
        self.ventana.iconbitmap("RecursosGraficos\\Logo_Slow_Icon_Map.ico")

        self.ancho = args[0].ancho
        self.alto = args[0].alto

        self.ventana.geometry("{0}x{1}".format(self.ancho, self.alto))
        self.DURACION = args[0].DURACION
        self.carros = args[0].carros

        self.construirFrames()

        # Finalmente añade los datos de la tabla anterior a la nueva tabla luego de creada
        for datos in self.carros:
            self.tabla.insert('', END, values=(datos[0], datos[1], datos[2]))

    def construirFrames(self):
        # Base Para Grafica, Botones y Tabla------------
        self.frame1 = Frame(self.ventana, background="white")
        self.frame1.config(width=str(int(self.ancho * 0.65)), height=self.alto)

        self.crearGrafico()

        self.frame2 = Frame(self.ventana, background="#F0F0F0")
        self.frame2.config(width=str(int(self.ancho * 0.35)), height=self.alto)

        self.estilarFrame2()

    def crearGrafico(self):
        # Crea el grafico con un unico subplot----------------
        self.grafica = Figure(figsize=((self.ancho * 0.65 / 100), (self.alto / 133.8)), dpi=100)
        self.area_dibujo = self.grafica.add_subplot(1, 1, 1)

        self.grafica.suptitle('Velocidades de Vehiculos')
        self.grafica.supxlabel("% Tiempo")
        self.grafica.supylabel("Velocidad(Km/h)")

    def estilarFrame2(self):
        # Añade estilo a la tabla de el frame2----------
        tipo_tabla = ttk.Style()
        tipo_tabla.map("Treeview", background=[("selected", "#76909c")])

        # Añade Tabla y boton al frame2-------------
        self.tabla = ttk.Treeview(self.frame2, columns=("#1", "#2", "#3"), height=int(self.alto / 22))
        self.tabla.pack(side=TOP)
        self.tabla.heading("#1", text="IdCarro")
        self.tabla.column("#1", width=int(self.ancho * 0.19 / 3), anchor="center")
        self.tabla.heading("#2", text="Velocidad")
        self.tabla.column("#2", width=int(self.ancho * 0.19 / 3), anchor="center")
        self.tabla.heading("#3", text="Infractor")
        self.tabla.column("#3", width=int(self.ancho * 0.19 / 3), anchor="center")

        self.boton2 = Button(self.frame2, text="Retroceder", command=self.ventana.destroy).pack(side=TOP)

    def guardarCarros(self, datos):
        # Recibe una lista de datos [ID,Velocidad,Infractor, Captura]
        # Guarda los datos del carro para luego graficarlos y los añade a la tabla----------
        self.carros.append([datos[0], datos[1], datos[2]])
        self.tabla.insert('', END, values=(datos[0], datos[1], datos[2]))

        # Añadir Funcion para Guardar a la base de datos el carro infractor///
        # El idvideo,idvia,multa ya están creados en el objeto al inicio ejecutar -> import ConexionBaseDeDatosSlow() as bD

        # conexionSlow = bD.ConexionBaseDeDatosSlow()
        # conexionSlow.cursorSlow.execute("INSERT INTO VEHICULOS (IDVIDEO,CAPTURA,IDVIA,VELOCIDADEXCEDIDA,MULTA,IDUSUARIO) VALUES ({0},{1},{2},{3},{4},{5})".format(self.idvideo,datos[3],self.idvia,datos[2],self.multa,self.idusuario))

        # ////

    def graficarYMostrar(self):
        self.graficar()

        # Añade y empaqueta los frames------------
        self.frame1.grid(row=0, column=0)
        self.tabla['show'] = 'headings'
        self.frame2.grid(row=0, column=1)

        # Añade y empaqueta el grafico al frame1 ----------
        canvas = FigureCanvasTkAgg(self.grafica, master=self.frame1)
        canvas.draw()
        canvas.get_tk_widget().pack(side=TOP)

        # Añade y empaqueta el widget enlazandolo con el grafico (varias opciones implementadas)---------
        barratareas = NavigationToolbar2Tk(canvas, self.frame1)
        barratareas.update()
        canvas._tkcanvas.pack(side=TOP)

        self.ventana.update()

    def graficar(self):
        # Grafica todos los carros guardados hasta ahora con una distancia entre datos fija-------
        distancia = (self.DURACION / len(self.carros))
        for i in range(len(self.carros) - 1):
            # Escoge un color aleatorio para cada carro
            col = "#%06x" % random.randint(0, 0xFFFFFF)
            self.area_dibujo.plot([0, self.DURACION], [self.carros[i][1], self.carros[i][1]], color=col)
            self.area_dibujo.text((i + 1) * distancia, (self.carros[i][1] - 0.5), self.carros[i][0], fontsize="small")