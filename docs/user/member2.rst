Parts Implemented by Mumtaz Cem Eris
====================================

**Logins and Moderators (users)**

First of all, to be able to enter website, you must sign up as a moderator. If you have already signed up, then you may login.
Without having logged in, you can not access to the website.
All passwords are stored in the database and they are all hashed. For more technical detail go to the developer guide.

   .. figure:: cem_ss/signup_page.png
      :scale: 50 %
      :alt: sign_up page

      Sign up page of ShakeSpace.

Below, you will see two screenshots from ShakeSpace. In the first one, you can see that someone tries to access to
imageposts page without having logged in. After that, ShakeSpace would redirect this person to the sign up page as
 it can be seen from the second screenshot.

   .. figure:: cem_ss/access_1.png
      :scale: 50 %
      :alt: unsuccessful access

      Unsuccessful access.
   .. figure:: cem_ss/access_2.png
      :scale: 50 %
      :alt: Redirection

      Redirection to the signup page.

Having signed up with the nickname 'mumtaz', after login ShakeSpace will welcome you. Now the visitor can post some posts,
 create events, check his/her profile and so on.

   .. figure:: cem_ss/welcome.PNG
      :scale: 50 %
      :alt: Welcome

Let's check mumtaz's profile. Here, the nickname of the current user and the other moderators are displayed.

   .. figure:: cem_ss/profile.PNG
      :scale: 50 %
      :alt: Profile

Apart from logins, I have created ImagePosts page as well. Well, you can not post an image, instead you can only post a text unfortunately.
 In this page, you can observe the image post feed that is all the image posts that have been posted.

   .. figure:: cem_ss/imageposts.PNG
      :scale: 50 %
      :alt: imageposts

Let's add an image post as 'mumtaz'.

   .. figure:: cem_ss/imageposts_add.PNG
      :scale: 50 %
      :alt: imageposts_add

'report.jpg' has been added by mumtaz. In the image post feed, you can see which moderator posted what along with their ids.

   .. figure:: cem_ss/imageposts_added.PNG
      :scale: 50 %
      :alt: imageposts_added

Update operation of 'report.jpg' to 'report.png'.

   .. figure:: cem_ss/update.PNG
      :scale: 50 %
      :alt: imageposts_update

It has been updated as 'report.png'.

   .. figure:: cem_ss/updated.PNG
      :scale: 50 %
      :alt: imageposts_updated

Now, let's delete 'report.png'.

   .. figure:: cem_ss/delete.PNG
      :scale: 50 %
      :alt: imageposts_delete

It has been deleted.

   .. figure:: cem_ss/deleted.PNG
      :scale: 50 %
      :alt: imageposts_deleted

If a moderator decides to log out, he/she can successfully log out by clicking Log Out link.
To be able to enter the site again, the moderator can click the link in the photo and it will direct to log in page.
The moderator should login again as well.

   .. figure:: cem_ss/logout.PNG
      :scale: 50 %
      :alt: logout

On the left screenshot, say the moderator ‘mumtaz’ decided to login again and ‘mumtaz’ is about to enter the nickname incorrectly.
On the right screenshot, it can be seen that the website handled it successfully.
It would be the same case if the moderator has typed his/her password incorrect as well.

   .. figure:: cem_ss/invalid_credentials.PNG
      :scale: 50 %
      :alt: invalid_credentials

If you are logged in as 'admin', then you can access the admin panel of moderators.
Other moderators can not see that nor access that.

   .. figure:: cem_ss/admin_panel.PNG
      :scale: 50 %
      :alt: admin_panel

In AdminPanel, admin can see all the moderators and can do operations on them such as adding, deleting or updating.
If a moderator who has posted an image post or image posts will be deleted, all of the image posts that has been posted by the moderator will be deleted as well.
Let's delete ‘mumtaz’ and see what happens.

   .. figure:: cem_ss/admin_panel2.PNG
      :scale: 50 %
      :alt: admin_panel2
   .. figure:: cem_ss/mumtaz.png
      :scale: 50 %
      :alt: mumtaz

Image posts before deletion operation of mumtaz.

   .. figure:: cem_ss/before_imgposts.PNG
      :scale: 50 %
      :alt: before

Removing mumtaz.

   .. figure:: cem_ss/mumtaz_delete.PNG
      :scale: 50 %
      :alt: mumtaz_delete

mumtaz has been deleted.

   .. figure:: cem_ss/mumtaz_deleted.PNG
      :scale: 50 %
      :alt: mumtaz_deleted

And after mumtaz has been deleted, all the image posts that posted by mumtaz have been deleted as well.

   .. figure:: cem_ss/mumtazs_posts_deleted.PNG
      :scale: 50 %
      :alt: mumtazs_posts_deleted

Let's update 'shakespeare'.

   .. figure:: cem_ss/shakespeare.PNG
      :scale: 50 %
      :alt: shakespeare

   .. figure:: cem_ss/shakespeare_update.PNG
      :scale: 50 %
      :alt: shakespeare

It has been updated.

   .. figure:: cem_ss/shakespeare_updated.PNG
      :scale: 50 %
      :alt: ahmet_hamdi_tanpinar