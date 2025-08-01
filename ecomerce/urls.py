
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from .views import AnuncioListView, HomeView, CreateAnuncioView, ChatListView, ChatDetailView, StartChatView, ProductDetailView, ProductUpdateView, SearchView, SearchResultsView, GetSubcategoriesView
from .views import AnuncioListView
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('create-anuncio/', CreateAnuncioView.as_view(), name='create_anuncio'),
    path('product/', AnuncioListView.as_view(), name='anuncio_list'),
    path('product/<int:product_id>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/<int:product_id>/edit/', ProductUpdateView.as_view(), name='product_update'),
    path('search/', SearchView.as_view(), name='search'),
    path('search-results/', SearchResultsView.as_view(), name='search_results'),
    path('get-subcategories/', GetSubcategoriesView.as_view(), name='get_subcategories'),
    path('chat/', ChatListView.as_view(), name='chat_list'),
    path('chat/<int:conversation_id>/', ChatDetailView.as_view(), name='chat_detail'),
    path('start-chat/<int:product_id>/', StartChatView.as_view(), name='start_chat'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)