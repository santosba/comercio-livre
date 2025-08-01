from asyncio.log import logger
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Category, Product, ProductPhoto, SubCategory, ChatConversation, ChatMessage
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.template.loader import render_to_string
import logging

# Create your views here.
class HomeView(TemplateView):
    template_name = 'ecomerce/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.select_related('user', 'category').prefetch_related('photos').order_by('-created_at')[:6]
        context['categories'] = Category.objects.prefetch_related('subcategories').all()
        return context

class CreateAnuncioView(LoginRequiredMixin,View):
    login_url ='login'
    template_name = 'ecomerce/create_anuncio.html'

    def get(self, request):
        categories = Category.objects.prefetch_related('subcategories').all()
        return render(request, self.template_name, {'categories': categories})

    def post(self, request):
        titulo = request.POST.get('titulo')
        categoria_id = request.POST.get('categoria_id')
        descricao = request.POST.get('descricao')
        imagens = request.FILES.getlist('imagens')
        price = request.POST.get('preco')

        # Check values in the screen (request.POST and request.FILES)
        
    
        # Validate inputs
        if not titulo or len(titulo) < 3:
            messages.error(request, 'O título deve ter pelo menos 3 caracteres.')
            return redirect('create_anuncio')

        if not categoria_id:
            messages.error(request, 'Por favor, selecione uma categoria.')
            return redirect('create_anuncio')

        if not descricao :
            messages.error(request, 'A descrição deve ter pelo menos 10 caracteres.')
            return redirect('create_anuncio')

        if len(imagens) > 5:
            messages.error(request, 'Você pode adicionar no máximo 5 imagens.')
            return redirect('create_anuncio')

        try:
            subcat = SubCategory.objects.get(id=categoria_id)
        except SubCategory.DoesNotExist:
            messages.error(request, 'Categoria inválida.')
            return redirect('create_anuncio')

        #print('price',price,flush=True)

        #return render(request, self.template_name, {'categories': Category.objects.prefetch_related('subcategories').all()})
        anuncio = Product.objects.create(
            name=titulo,
            category=subcat.category,
            description=descricao,
            user=request.user,
            price =float(price),
            created_at=timezone.now(),
            data_expiracao_anuncio=timezone.now() + timezone.timedelta(days=27)
        )

        unique_images = set()
        for imagem in imagens:
            if imagem.name in unique_images:
                messages.error(request, f'A imagem "{imagem.name}" está duplicada.')
                return redirect('create_anuncio')  # Stop processing and redirect immediately
            unique_images.add(imagem.name)
            ProductPhoto.objects.create(
                product=anuncio,
                image=imagem
            )

        messages.success(request, 'Anúncio criado com sucesso!')
        return redirect('home')
    


class AnuncioListView(LoginRequiredMixin,ListView):
    login_url = 'login'
    model = Product
    template_name = 'ecomerce/anuncio_list.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        return Product.objects.select_related('user', 'category').prefetch_related('photos').filter(user=self.request.user).order_by('-created_at')

@method_decorator(login_required, name='dispatch')
class ChatListView(LoginRequiredMixin,View):
    login_url = 'login'
    template_name = 'ecomerce/chat_list.html'
    
    def get(self, request):
        # Get all conversations for the current user
        conversations = ChatConversation.objects.filter(
            Q(buyer=request.user) | Q(seller=request.user)
        ).select_related('product', 'buyer', 'seller').order_by('-updated_at')

        # Add pagination
        paginator = Paginator(conversations, 10)  # Show 10 conversations per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, self.template_name, {'page_obj': page_obj,'conversations': conversations})

@method_decorator(login_required, name='dispatch')
class ChatDetailView(LoginRequiredMixin,View):
    login_url = 'login'
    template_name = 'ecomerce/chat_detail.html'
    
    def get(self, request, conversation_id):
        conversation = get_object_or_404(
            ChatConversation, 
            id=conversation_id
        )
        
        # Check if user is part of this conversation
        if conversation.buyer != request.user and conversation.seller != request.user:
            messages.error(request, 'Você não tem permissão para acessar esta conversa.')
            return redirect('chat_list')
        
        # Mark messages as read for the current user
        ChatMessage.objects.filter(
            conversation=conversation,
            is_read=False
        ).exclude(sender=request.user).update(is_read=True)
        
        messages = conversation.messages.select_related('sender').all()
        
        return render(request, self.template_name, {
            'conversation': conversation,
            'messages': messages
        })
    
    def post(self, request, conversation_id):
        conversation = get_object_or_404(
            ChatConversation, 
            id=conversation_id
        )
        
        # Check if user is part of this conversation
        if conversation.buyer != request.user and conversation.seller != request.user:
            messages.error(request, 'Você não tem permissão para acessar esta conversa.')
            return redirect('chat_list')
        
        message_text = request.POST.get('message', '').strip()
        if message_text:
            ChatMessage.objects.create(
                conversation=conversation,
                sender=request.user,
                message=message_text
            )
            conversation.updated_at = timezone.now()
            conversation.save()
        
        return redirect('chat_detail', conversation_id=conversation_id)

@method_decorator(login_required, name='dispatch')
class StartChatView(LoginRequiredMixin,View):
    login_url = 'login'
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        
        # Check if user is trying to chat with themselves
        if product.user == request.user:
            messages.error(request, 'Você não pode conversar sobre seu próprio produto.')
            return redirect('product_detail', product_id=product_id)
        
        # Get or create conversation
        conversation, created = ChatConversation.objects.get_or_create(
            product=product,
            buyer=request.user,
            seller=product.user,
            defaults={'is_active': True}
        )
        
        return redirect('chat_detail', conversation_id=conversation.id)

class ProductDetailView(LoginRequiredMixin,DetailView):
    login_url = 'login'
    template_name = 'ecomerce/product_detail.html'
    model = Product
    context_object_name = 'product'

    def get_object(self, queryset=None):
        product_id = self.kwargs.get('product_id')
        return get_object_or_404(Product, id=product_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photos'] = self.object.photos.all()
        return context

@method_decorator(login_required, name='dispatch')
class ProductUpdateView(LoginRequiredMixin,View):
    login_url = 'login'
    template_name = 'ecomerce/product_update.html'

    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id, user=request.user)
        categories = Category.objects.prefetch_related('subcategories').all()
        return render(request, self.template_name, {
            'product': product,
            'categories': categories,
            'photos': product.photos.all()
        })

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id, user=request.user)
        
        titulo = request.POST.get('titulo')
        categoria_id = request.POST.get('categoria_id')
        descricao = request.POST.get('descricao')
        imagens = request.FILES.getlist('imagens')
        price = request.POST.get('preco')
        delete_photos = request.POST.getlist('delete_photos')

        # Validate inputs
        if not titulo or len(titulo) < 3:
            messages.error(request, 'O título deve ter pelo menos 3 caracteres.')
            return redirect('product_update', product_id=product_id)

        if not categoria_id:
            messages.error(request, 'Por favor, selecione uma categoria.')
            return redirect('product_update', product_id=product_id)

        if not descricao:
            messages.error(request, 'A descrição deve ter pelo menos 10 caracteres.')
            return redirect('product_update', product_id=product_id)

        try:
            subcat = SubCategory.objects.get(id=categoria_id)
        except SubCategory.DoesNotExist:
            messages.error(request, 'Categoria inválida.')
            return redirect('product_update', product_id=product_id)

        # Update product fields
        product.name = titulo
        product.category = subcat.category
        product.description = descricao
        product.price = float(price)
        product.save()

        # Delete selected photos
        if delete_photos:
            ProductPhoto.objects.filter(id__in=delete_photos, product=product).delete()

        # Add new photos
        if imagens:
            current_photos_count = product.photos.count()
            if current_photos_count + len(imagens) > 5:
                messages.error(request, f'Você pode ter no máximo 5 imagens. Atualmente você tem {current_photos_count} imagens.')
                return redirect('product_update', product_id=product_id)

            unique_images = set()
            for imagem in imagens:
                if imagem.name in unique_images:
                    messages.error(request, f'A imagem "{imagem.name}" está duplicada.')
                    return redirect('product_update', product_id=product_id)
                unique_images.add(imagem.name)
                ProductPhoto.objects.create(
                    product=product,
                    image=imagem
                )

        messages.success(request, 'Produto atualizado com sucesso!')
        return redirect('product_detail', product_id=product_id)

class SearchView(LoginRequiredMixin,View):
    login_url = 'login'
    template_name = 'ecomerce/search.html'
    
    def get(self, request):
        categories = Category.objects.prefetch_related('subcategories').all()
        initial_query = request.GET.get('q', '')
        initial_category = request.GET.get('category', '')
        return render(request, self.template_name, {
            'categories': categories,
            'initial_query': initial_query,
            'initial_category': initial_category
        })

class SearchResultsView(LoginRequiredMixin,View):
    login_url = 'login'

    def get(self, request):
        # Get search parameters
        query = request.GET.get('q', '').strip()
        category_id = request.GET.get('category', '')
        subcategory_id = request.GET.get('subcategory', '')
        min_price = request.GET.get('min_price', '')
        max_price = request.GET.get('max_price', '')
        page = request.GET.get('page', 1)
        
        # Start with all products
        products = Product.objects.select_related('user', 'category').prefetch_related('photos').all()
        
        # Apply filters
        if query:
            products = products.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query)
            )
        
        if category_id:
            products = products.filter(category_id=category_id)
        
        if subcategory_id:
            try:
                subcategory = SubCategory.objects.get(id=subcategory_id)
                products = products.filter(category=subcategory.category)
            except SubCategory.DoesNotExist:
                pass
        
        if min_price:
            try:
                products = products.filter(price__gte=float(min_price))
            except ValueError:
                pass
        
        if max_price:
            try:
                products = products.filter(price__lte=float(max_price))
            except ValueError:
                pass
        
        # Order by newest first
        products = products.order_by('-created_at')
        
        # Pagination
        paginator = Paginator(products, 12)  # 12 products per page
        page_obj = paginator.get_page(page)
        
        # Get category name for display
        category_name = ""
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                category_name = category.name
            except Category.DoesNotExist:
                pass
        
        # Render the results template
        html = render_to_string('ecomerce/search_results.html', {
            'page_obj': page_obj,
            'query': query,
            'category_name': category_name,
            'total_count': products.count()
        })
        
        return JsonResponse({
            'html': html,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'current_page': page_obj.number,
            'total_pages': page_obj.paginator.num_pages,
            'total_count': products.count()
        })

class GetSubcategoriesView(LoginRequiredMixin,View):
    login_url = 'login'
    def get(self, request):
        category_id = request.GET.get('category_id')
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                subcategories = category.subcategories.all()
                data = [{'id': sub.id, 'name': sub.name} for sub in subcategories]
                return JsonResponse({'subcategories': data})
            except Category.DoesNotExist:
                pass
        return JsonResponse({'subcategories': []})