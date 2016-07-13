import React from 'react';

class Footer extends React.Component {
    render() {
        return (
            <footer>
                <a href="https://www.holderdeord.no/">
                    <img className="logo" src="/logo.png" />
                </a>

                <h4>Holder de ord &copy; 2014 - {new Date().getFullYear()}</h4>
            </footer>
        );
    }
}

module.exports = Footer;
