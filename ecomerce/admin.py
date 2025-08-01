from django.contrib import admin
from .models import Category, SubCategory, Product, ProductPhoto, ChatConversation, ChatMessage
from .forms import SubCategoryForm

# Register your models here.
admin.site.register(Category)

class subCategoryAdmin(admin.ModelAdmin):
    form = SubCategoryForm
    list_display = ('name', 'description', 'category')
    search_fields = ('name',)
    fieldsets = (
        (None, {
            'fields': ('category', 'name', 'description', )
        }),
    )
admin.site.register(SubCategory, subCategoryAdmin)  

admin.site.register(Product)
admin.site.register(ProductPhoto)

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('sender', 'message', 'is_read', 'created_at')

class ChatConversationAdmin(admin.ModelAdmin):
    list_display = ('product', 'buyer', 'seller', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('product__name', 'buyer__email', 'seller__email')
    inlines = [ChatMessageInline]
    readonly_fields = ('created_at', 'updated_at')

class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'sender', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('message', 'sender__email')
    readonly_fields = ('created_at',)

admin.site.register(ChatConversation, ChatConversationAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)