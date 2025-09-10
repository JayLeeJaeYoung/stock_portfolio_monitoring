var dagcomponentfuncs = (window.dashAgGridComponentFunctions =
  window.dashAgGridComponentFunctions || {});

dagcomponentfuncs.YahooLink = function (props) {
  const ticker = props.data.symbol;

  return React.createElement(
    "a",
    {
      href: "https://redacted_website.com/" + ticker + "/",
      target: "_blank",
      rel: "noopener noreferrer",
    },
    props.value
  );
};

dagcomponentfuncs.IconButton = function (props) {
  let n_clicks = 0;

  function onClick() {
    n_clicks++;

    props.setData({
      n_clicks: n_clicks,
    });
  }

  const icon = props.icon
    ? React.createElement(window.dash_iconify.DashIconify, {
        icon: props.icon,
        style: {
          width: "100%",
          height: "100%",
        },
      })
    : null;

  return React.createElement(
    "div",
    {
      style: {
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        height: "100%",
        width: "100%",
        padding: 0,
        margin: 0,
      },
    },
    React.createElement(
      window.dash_mantine_components.Button,
      {
        onClick,
        variant: "outline",
        color: "blue",
        radius: "md",
        style: {
          width: "30px",
          height: "30px",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          padding: "5px",
          margin: 0,
        },
      },
      icon
    )
  );
};

dagcomponentfuncs.AlertButton = function (props) {
  let n_clicks = 0;

  function onClick() {
    n_clicks++;
    props.setData({
      n_clicks: n_clicks,
    });
  }

  const icon = props.icon
    ? React.createElement(window.dash_iconify.DashIconify, {
        icon: props.icon,
        style: {
          width: "100%",
          height: "100%",
        },
      })
    : null;

  // Get alertCount from props.data, default to 0 if missing
  const alertCount =
    props.data && props.data.alertCount ? props.data.alertCount : 0;

  const badge =
    alertCount > 0
      ? React.createElement(
          "div",
          {
            style: {
              position: "absolute",
              bottom: "2px",
              left: "2px",
              backgroundColor: "red",
              color: "white",
              borderRadius: "50%",
              width: "12px",
              height: "12px",
              fontSize: "8px",
              fontWeight: "bold",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              pointerEvents: "none", // badge does not block clicks
              userSelect: "none",
              zIndex: 10,
            },
          },
          alertCount > 99 ? "99+" : alertCount // cap display if too many alerts
        )
      : null;

  return React.createElement(
    "div",
    {
      style: {
        position: "relative", // needed for badge absolute positioning
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        height: "100%",
        width: "100%",
        padding: 0,
        margin: 0,
      },
    },
    React.createElement(
      window.dash_mantine_components.Button,
      {
        onClick,
        variant: "outline",
        color: "blue",
        radius: "md",
        style: {
          width: "30px",
          height: "30px",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          padding: "5px",
          margin: 0,
          position: "relative", // for icon inside button
        },
      },
      icon,
      badge
    )
  );
};
