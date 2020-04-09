$(function () {
  $(document).scroll(function () {
    var $nav = $(".navbar.fixed-top");
    $nav.toggleClass('scrolled', $(this).scrollTop() > $nav.height())
        .toggleClass('shadow', $(this).scrollTop() > $nav.height());
  });
});