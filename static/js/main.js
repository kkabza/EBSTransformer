// Add submenu toggle functionality
document.addEventListener('DOMContentLoaded', function() {
  // Initialize sidebar submenus
  const sidebarItems = document.querySelectorAll('.sidebar-menu > li');
  
  // Show submenus of active items by default
  sidebarItems.forEach(item => {
    if (item.classList.contains('active')) {
      const submenu = item.querySelector('.submenu');
      if (submenu) {
        submenu.style.display = 'block';
      }
    }
  });

  // Add click event for menu items with submenus
  sidebarItems.forEach(item => {
    const submenu = item.querySelector('.submenu');
    if (submenu) {
      // Add click listener to parent item
      const parentLink = item.querySelector('a');
      parentLink.addEventListener('click', function(e) {
        // Check if clicked directly on the link (not on submenu)
        if (e.target === parentLink || e.target.closest('a') === parentLink) {
          if (window.innerWidth < 992) { // Only toggle on mobile/tablet
            e.preventDefault();
            submenu.style.display = submenu.style.display === 'block' ? 'none' : 'block';
          }
        }
      });
    }
  });
});

// Rest of your existing JavaScript... 