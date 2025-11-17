import React, { useState, useEffect } from 'react';
import { Search, Filter, BookOpen, Calendar, User, ShoppingCart, AlertCircle, Check, X } from 'lucide-react';

// Configuración de la API
const API_BASE_URL = 'http://localhost:8000/api/v1';

const BibliotecaCatalogo = () => {
  // Estados principales
  const [documentos, setDocumentos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Estados de búsqueda y filtros
  const [searchTerm, setSearchTerm] = useState('');
  const [categoriaSeleccionada, setCategoriaSeleccionada] = useState(null);
  const [paginaActual, setPaginaActual] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const itemsPorPagina = 6;
  
  // Carrito de libros
  const [carrito, setCarrito] = useState([]);
  const [mostrarCarrito, setMostrarCarrito] = useState(false);

  // Cargar categorías al inicio
  useEffect(() => {
    cargarCategorias();
  }, []);

  // Cargar documentos cuando cambian los filtros
  useEffect(() => {
    if (searchTerm) {
      buscarDocumentos();
    } else if (categoriaSeleccionada) {
      buscarPorCategoria();
    } else {
      cargarDocumentos();
    }
  }, [paginaActual, categoriaSeleccionada]);

  const cargarCategorias = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/categorias/`);
      const data = await response.json();
      // Asegurarse de que sea un array
      setCategorias(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Error cargando categorías:', err);
      setCategorias([]); // Array vacío en caso de error
    }
  };

  const cargarDocumentos = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `${API_BASE_URL}/documentos/?page=${paginaActual}&size=${itemsPorPagina}`
      );
      const data = await response.json();
      setDocumentos(data.items || []);
      setTotalItems(data.total_items || 0);
    } catch (err) {
      setError('Error al cargar los documentos');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const buscarDocumentos = async () => {
    if (!searchTerm.trim()) {
      cargarDocumentos();
      return;
    }
    
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `${API_BASE_URL}/catalogo/buscar/?q=${encodeURIComponent(searchTerm)}&page=${paginaActual}&size=${itemsPorPagina}`
      );
      const data = await response.json();
      setDocumentos(data.items || []);
      setTotalItems(data.total_items || 0);
    } catch (err) {
      setError('Error en la búsqueda');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const buscarPorCategoria = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `${API_BASE_URL}/categorias/${categoriaSeleccionada}/documentos/?page=${paginaActual}&size=${itemsPorPagina}`
      );
      const data = await response.json();
      setDocumentos(data.items || []);
      setTotalItems(data.total_items || 0);
    } catch (err) {
      setError('Error al filtrar por categoría');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const obtenerDisponibilidad = async (documentoId) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/ejemplares/documento/${documentoId}/disponibilidad`
      );
      return await response.json();
    } catch (err) {
      console.error('Error obteniendo disponibilidad:', err);
      return { disponibles: 0, total: 0, puede_solicitar: false };
    }
  };

  // Funciones del carrito
  const agregarAlCarrito = (documento) => {
    if (carrito.find(item => item.id === documento.id)) {
      alert('Este libro ya está en tu carrito');
      return;
    }
    setCarrito([...carrito, documento]);
  };

  const removerDelCarrito = (documentoId) => {
    setCarrito(carrito.filter(item => item.id !== documentoId));
  };

  const limpiarCarrito = () => {
    setCarrito([]);
  };

  // Funciones de UI
  const handleSearchSubmit = () => {
    setPaginaActual(1);
    buscarDocumentos();
  };

  const handleCategoriaClick = (categoria) => {
    if (categoriaSeleccionada === categoria) {
      setCategoriaSeleccionada(null);
    } else {
      setCategoriaSeleccionada(categoria);
      setSearchTerm('');
    }
    setPaginaActual(1);
  };

  const limpiarFiltros = () => {
    setSearchTerm('');
    setCategoriaSeleccionada(null);
    setPaginaActual(1);
  };

  const totalPaginas = Math.ceil(totalItems / itemsPorPagina);

  // Componente de tarjeta de libro
  const LibroCard = ({ documento }) => {
    const [disponibilidad, setDisponibilidad] = useState(null);
    const [cargandoDisp, setCargandoDisp] = useState(true);

    useEffect(() => {
      const cargarDisponibilidad = async () => {
        setCargandoDisp(true);
        const disp = await obtenerDisponibilidad(documento.id);
        setDisponibilidad(disp);
        setCargandoDisp(false);
      };
      cargarDisponibilidad();
    }, [documento.id]);

    const getDisponibilidadColor = () => {
      if (!disponibilidad) return 'bg-gray-500';
      if (disponibilidad.disponibles === 0) return 'bg-red-500';
      if (disponibilidad.disponibles <= 2) return 'bg-yellow-500';
      return 'bg-green-500';
    };

    return (
      <div className="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 overflow-hidden">
        <div className="p-6">
          {/* Header con tipo de documento */}
          <div className="flex justify-between items-start mb-4">
            <span className="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-semibold rounded-full">
              {documento.tipo.toUpperCase()}
            </span>
            {!cargandoDisp && disponibilidad && (
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${getDisponibilidadColor()}`}></div>
                <span className="text-sm text-gray-600">
                  {disponibilidad.disponibles}/{disponibilidad.total}
                </span>
              </div>
            )}
          </div>

          {/* Título y Autor */}
          <h3 className="text-xl font-bold text-gray-900 mb-2 line-clamp-2 min-h-[56px]">
            {documento.titulo}
          </h3>
          <p className="text-gray-600 mb-4 flex items-center gap-2">
            <User size={16} />
            {documento.autor}
          </p>

          {/* Información adicional */}
          <div className="space-y-2 mb-4 text-sm text-gray-700">
            {documento.anio && (
              <p className="flex items-center gap-2">
                <Calendar size={16} />
                Año: {documento.anio}
              </p>
            )}
            {documento.editorial && (
              <p className="flex items-center gap-2">
                <BookOpen size={16} />
                {documento.editorial}
              </p>
            )}
            {documento.categoria && (
              <p>
                <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs">
                  {documento.categoria.replace(/_/g, ' ')}
                </span>
              </p>
            )}
          </div>

          {/* Estado de disponibilidad */}
          <div className="mb-4">
            {cargandoDisp ? (
              <p className="text-sm text-gray-500">Verificando disponibilidad...</p>
            ) : disponibilidad ? (
              <div className="space-y-1">
                <p className="text-sm font-semibold">
                  {disponibilidad.puede_solicitar ? (
                    <span className="text-green-600 flex items-center gap-1">
                      <Check size={16} /> Disponible para préstamo
                    </span>
                  ) : (
                    <span className="text-red-600 flex items-center gap-1">
                      <X size={16} /> No disponible actualmente
                    </span>
                  )}
                </p>
                <p className="text-xs text-gray-600">
                  Disponibles: {disponibilidad.disponibles} | 
                  Prestados: {disponibilidad.prestados} |
                  En sala: {disponibilidad.en_sala}
                </p>
              </div>
            ) : null}
          </div>

          {/* Botón de agregar */}
          <button
            onClick={() => agregarAlCarrito(documento)}
            disabled={!disponibilidad?.puede_solicitar}
            className={`w-full py-2 px-4 rounded-lg font-semibold transition-colors duration-200 flex items-center justify-center gap-2 ${
              disponibilidad?.puede_solicitar
                ? 'bg-green-500 hover:bg-green-600 text-white'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            {carrito.find(item => item.id === documento.id) ? (
              <>
                <Check size={18} />
                En el carrito
              </>
            ) : (
              <>
                <ShoppingCart size={18} />
                Agregar
              </>
            )}
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <BookOpen size={40} />
              <div>
                <h1 className="text-3xl font-bold">Biblioteca de Estación Central</h1>
                <p className="text-blue-100">Consulta y solicita libros</p>
              </div>
            </div>
            <button
              onClick={() => setMostrarCarrito(!mostrarCarrito)}
              className="relative bg-white text-blue-600 px-4 py-2 rounded-lg font-semibold hover:bg-blue-50 transition-colors flex items-center gap-2"
            >
              <ShoppingCart size={20} />
              Carrito
              {carrito.length > 0 && (
                <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center">
                  {carrito.length}
                </span>
              )}
            </button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Barra de búsqueda */}
        <div className="mb-8">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearchSubmit()}
                placeholder="Buscar por título o autor..."
                className="w-full pl-10 pr-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none text-lg"
              />
            </div>
            <button
              onClick={handleSearchSubmit}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              Buscar
            </button>
            {(searchTerm || categoriaSeleccionada) && (
              <button
                onClick={limpiarFiltros}
                className="bg-gray-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-gray-600 transition-colors"
              >
                Limpiar
              </button>
            )}
          </div>
        </div>

        <div className="flex gap-8">
          {/* Sidebar de filtros */}
          <aside className="w-64 flex-shrink-0">
            <div className="bg-white rounded-lg shadow-md p-6 sticky top-4">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Filter size={20} />
                Filtros de Búsqueda
              </h2>
              
              <div className="space-y-2">
                <h3 className="font-semibold text-gray-700 mb-2">Categorías</h3>
                {categorias.length === 0 ? (
                  <p className="text-sm text-gray-500">Cargando categorías...</p>
                ) : (
                  categorias.map((cat) => (
                    <button
                      key={cat.categoria}
                      onClick={() => handleCategoriaClick(cat.categoria)}
                      className={`w-full text-left px-4 py-2 rounded-lg transition-colors ${
                        categoriaSeleccionada === cat.categoria
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                      }`}
                    >
                      <div className="flex justify-between items-center">
                        <span className="capitalize">
                          {cat.categoria.replace(/_/g, ' ')}
                        </span>
                        <span className="text-sm">({cat.conteo})</span>
                      </div>
                    </button>
                  ))
                )}
              </div>
            </div>
          </aside>

          {/* Área principal de contenido */}
          <main className="flex-1">
            {/* Información de resultados */}
            <div className="mb-6 flex justify-between items-center">
              <p className="text-gray-700">
                {loading ? (
                  'Cargando...'
                ) : (
                  <>
                    Mostrando <strong>{documentos.length}</strong> de{' '}
                    <strong>{totalItems}</strong> documentos
                    {searchTerm && ` para "${searchTerm}"`}
                    {categoriaSeleccionada && ` en categoría "${categoriaSeleccionada}"`}
                  </>
                )}
              </p>
            </div>

            {/* Error */}
            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6 flex items-center gap-2">
                <AlertCircle size={20} />
                {error}
              </div>
            )}

            {/* Grid de libros */}
            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="bg-white rounded-lg shadow-md p-6 animate-pulse">
                    <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
                    <div className="h-6 bg-gray-200 rounded w-3/4 mb-2"></div>
                    <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
                    <div className="space-y-2 mb-4">
                      <div className="h-3 bg-gray-200 rounded"></div>
                      <div className="h-3 bg-gray-200 rounded"></div>
                    </div>
                    <div className="h-10 bg-gray-200 rounded"></div>
                  </div>
                ))}
              </div>
            ) : documentos.length === 0 ? (
              <div className="text-center py-16">
                <BookOpen size={64} className="mx-auto text-gray-400 mb-4" />
                <h3 className="text-2xl font-semibold text-gray-700 mb-2">
                  No se encontraron documentos
                </h3>
                <p className="text-gray-500">
                  Intenta con otros términos de búsqueda o filtros
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {documentos.map((doc) => (
                  <LibroCard key={doc.id} documento={doc} />
                ))}
              </div>
            )}

            {/* Paginación */}
            {totalPaginas > 1 && (
              <div className="mt-8 flex justify-center gap-2">
                <button
                  onClick={() => setPaginaActual(Math.max(1, paginaActual - 1))}
                  disabled={paginaActual === 1}
                  className="px-4 py-2 bg-white border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  Anterior
                </button>
                
                {[...Array(totalPaginas)].map((_, i) => {
                  const pagina = i + 1;
                  if (
                    pagina === 1 ||
                    pagina === totalPaginas ||
                    (pagina >= paginaActual - 1 && pagina <= paginaActual + 1)
                  ) {
                    return (
                      <button
                        key={pagina}
                        onClick={() => setPaginaActual(pagina)}
                        className={`px-4 py-2 rounded-lg ${
                          paginaActual === pagina
                            ? 'bg-blue-600 text-white'
                            : 'bg-white border border-gray-300 hover:bg-gray-50'
                        }`}
                      >
                        {pagina}
                      </button>
                    );
                  } else if (
                    pagina === paginaActual - 2 ||
                    pagina === paginaActual + 2
                  ) {
                    return <span key={pagina} className="px-2">...</span>;
                  }
                  return null;
                })}
                
                <button
                  onClick={() => setPaginaActual(Math.min(totalPaginas, paginaActual + 1))}
                  disabled={paginaActual === totalPaginas}
                  className="px-4 py-2 bg-white border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  Siguiente
                </button>
              </div>
            )}
          </main>
        </div>
      </div>

      {/* Modal del carrito */}
      {mostrarCarrito && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden flex flex-col">
            <div className="bg-blue-600 text-white p-6 flex justify-between items-center">
              <h2 className="text-2xl font-bold flex items-center gap-2">
                <ShoppingCart size={28} />
                Tu Carrito ({carrito.length})
              </h2>
              <button
                onClick={() => setMostrarCarrito(false)}
                className="text-white hover:bg-blue-700 rounded-full p-2"
              >
                <X size={24} />
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6">
              {carrito.length === 0 ? (
                <div className="text-center py-12">
                  <ShoppingCart size={64} className="mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-600 text-lg">Tu carrito está vacío</p>
                  <p className="text-gray-500">Agrega libros para solicitar</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {carrito.map((libro) => (
                    <div
                      key={libro.id}
                      className="flex justify-between items-start p-4 bg-gray-50 rounded-lg"
                    >
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg">{libro.titulo}</h3>
                        <p className="text-gray-600">{libro.autor}</p>
                        <span className="text-xs text-gray-500">{libro.tipo}</span>
                      </div>
                      <button
                        onClick={() => removerDelCarrito(libro.id)}
                        className="text-red-500 hover:text-red-700 p-2"
                      >
                        <X size={20} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            {carrito.length > 0 && (
              <div className="border-t p-6 bg-gray-50">
                <button
                  onClick={() => {
                    alert('Funcionalidad de solicitud en desarrollo');
                  }}
                  className="w-full bg-green-500 text-white py-3 rounded-lg font-bold text-lg hover:bg-green-600 transition-colors mb-3"
                >
                  Solicitar Libros ({carrito.length})
                </button>
                <button
                  onClick={limpiarCarrito}
                  className="w-full bg-gray-500 text-white py-2 rounded-lg hover:bg-gray-600 transition-colors"
                >
                  Vaciar Carrito
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default BibliotecaCatalogo;