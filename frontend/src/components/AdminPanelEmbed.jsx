import React from 'react';

const AdminPanelEmbed = () => {
  return (
    <div style={{ width: '100vw', height: '100vh', margin: 0, padding: 0 }}>
      <iframe 
        src="https://panneau-production.up.railway.app" 
        style={{ 
          width: '100%', 
          height: '100%', 
          border: 'none',
          margin: 0,
          padding: 0
        }}
        title="Panneau d'administration"
      />
    </div>
  );
};

export default AdminPanelEmbed;
