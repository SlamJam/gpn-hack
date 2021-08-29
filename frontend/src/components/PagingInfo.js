import PropTypes from "prop-types";
import React from "react";

import { default as appendClassName } from "./appendClassName";

function PagingInfo({
  className,
  end,
  searchTerm,
  start,
  totalResults,
  ...rest
}) {
  return (
    <div className={appendClassName("sui-paging-info", className)} {...rest}>
      Показано{" "}
      <strong>
        {start} - {end}
      </strong>{" "}
      из <strong>{totalResults}</strong>
      {searchTerm && (
        <>
          {" "}
          для запроса: <em>{searchTerm}</em>
        </>
      )}
    </div>
  );
}

PagingInfo.propTypes = {
  end: PropTypes.number.isRequired,
  searchTerm: PropTypes.string.isRequired,
  start: PropTypes.number.isRequired,
  totalResults: PropTypes.number.isRequired,
  className: PropTypes.string
};

export default PagingInfo;
