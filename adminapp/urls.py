from django.urls import path
from adminapp import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns =[
    path('signup/',views.signup,name='signup'),
    path("adminlogin/", views.adminlogin, name="adminlogin"),
    path("verify_otp/", views.verify_otp, name="verify_otp"),
    path("admin_profile/",views.admin_profile,name="admin_profile"),
    path("change-admin-password/",views.change_admin_password,name="change_admin_password"),
    path("edit-admin-profile/",views.edit_admin_profile,name="edit_admin_profile"),

    path("forgot-admin-password/",views.forgot_admin_password,name="forgot_admin_password"),
    path("verify-admin-forgot-otp/",views.verify_admin_forgot,name="verify_admin_forgot"),
    path("reset-admin-password/",views.reset_admin_password,name="reset_admin_password"),
    
    path("dashboard/", views.dashboard, name="dashboard"),
    path("adminlogout/", views.adminlogout, name="adminlogout"),
    path('category/',views.add_Category,name='category'),
    path('add_subcategory/',views.add_subcategory,name='add_subcategory'),
    path('view_category/',views.View_Category,name='view_category'),
    path('sub_category_view/', views.ViewSubCategory, name='sub_category_view'),
    path('edit_category/<int:id>/',views.Edit_Category,name='edit_category'),
    path('editSubCategory/<int:id>/',views.EditSubCategory,name='editSubCategory'),
    path('delete_category/<int:id>/', views.Delete_Category, name='delete_category'),
    path('multiple_delete_category/', views.Multiple_Delete_Category, name='multiple_delete_category'),
    path('delete_all_category/', views.Delete_All_Category, name='delete_all_category'),


    path("load_subcategory/", views.load_subcategory, name="load_subcategory"),

    path("load_brand/", views.load_brand, name="load_brand"),

    path('deleteSubCategory/<int:id>/', views.DeleteSubCategory, name='deleteSubCategory'),
    path('multiple_delete_subcategory/', views.Multiple_Delete_SubCategory, name='multiple_delete_subcategory'),
    path('delete_all_subcategory/', views.Delete_All_SubCategory, name='delete_all_subcategory'), 

    #Brands
    path("brand/", views.Add_Brand, name="brand"),
    path("view_brand/", views.View_Brand, name="view_brand"),
    path("edit_brand/<int:id>/", views.Edit_Brand, name="edit_brand"),
    path("delete_brand/<int:id>/", views.Delete_Brand, name="delete_brand"),
    path("multiple_delete_brand/", views.Multiple_Delete_Brand, name="multiple_delete_brand"),
    path("delete_all_brand/", views.Delete_All_Brand, name="delete_all_brand"),

    #Products

    path("add_product/", views.Add_Product, name="add_product"),
    path("view_product/", views.View_Product, name="view_product"),
    path('edit_product/<int:id>/', views.Edit_Product, name='edit_product'),
    path('delete_product/<int:id>/', views.Delete_Product, name='delete_product'),
    path('multiple_delete_product/', views.Multiple_Delete_Product, name='multiple_delete_product'),
    path('delete_all_product/', views.Delete_All_Product, name='delete_all_product'),
    path("load-subcategory/", views.load_subcategory, name="load_subcategory"),
    path("admin_orders/", views.admin_orders, name="admin_orders"), 
    path("update-order-status/<int:order_id>/",views.update_order_status,name="update_order_status"),
    path('users/',views.users,name='users'),
    path("admin-cancel-order/<int:order_id>/",views.admin_cancel_order,name="admin_cancel_order"),
    path("block-unblock-users/",views.block_unblock_users,name="block_unblock_users"),
    path("toggle-user-status/<int:user_id>/",views.toggle_user_status,name="toggle_user_status"),
    path("delete-users/",views.delete_users,name="delete_users"),
    path("delete-user/<int:user_id>/",views.delete_user,name="delete_user"),
    path("user-roles/",views.user_roles,name="user_roles"),
    path("update-user-role/<int:user_id>/",views.update_user_role,name="update_user_role"),
    path("view-messages/",views.view_messages,name="view_messages"),
    path("reply-message/<int:id>/",views.reply_message,name="reply_message"),
    path("delete-message/<int:id>/",views.delete_message,name="delete_message"),
  






]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root = settings.MEDIA_ROOT
    )