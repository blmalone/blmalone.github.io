---
layout: post
title: Twelve Expensive Words
date: 2017-08-30 11:12:00-0400
---

<div class="container">
			<div class="row">
				<div class="col-lg-12 text-center">
					<h3>Twelve Expensive Words - 30/08/17</h3>
				</div>
			</div>
			<div class="row justify-content-center">
				<div class="col-lg-12">
					The thought of financial independence is an attractive prospect for any recent graduate. I've observed over the last six months, that many advertisers are using cryptocurrenices to push similar promises. Particulary to those people with a bitcoin related term in their cookie history.<br>
					In my case, I was hit with these adverts long after I’d initially invested. I mined four Ethereum when the price was around £10/ETH. Back then cryptocurrencies weren’t the most popular place to put your money. Mainly due to the negative media coverage spawning from black swan events that affected Bitcoin a few years prior.<br><br>
					I’d been developing with Ethereum both independently and professionally before making the investment. In retrospect, my small investment in Ethereum was a by-product of understanding the platform's potential. I had a quite confidence that it would continue to grow.<br> In this post you should get an understanding of how to <i>recover a Jaxx wallet's credentials</i> if you've forgot/lost them.<br><br>

					<a class="link" href="https://etherchain.org/account/0x9393c36b0869f70c89d99be4b2a77f9fef710d59" target="_blank">My Dormant Ethereum Address</a><br>
					Any pay-outs from my mining hardware were sent to the account displayed in the above link. This account was managed through a <a class="link" href="https://jaxx.io/" target="_blank">Jaxx</a> wallet and backed up by a 12-word seed phrase. The first piece of advice you receive from Jaxx is to store your 12-words securely and don’t lose them or you’ll lose your funds. Now, notice how I haven’t created any outgoing transactions from this account? Well…<br><br>

					Cutting a long story short, I unknowingly saved my 12-word phrase in a place that I inevitably wouldn’t have access to. More specifically, in an old work laptop that had to be returned. <br>
					Since then, I’ve exhausted every possible avenue that's presented some a reasonable probability of success. Additionally, I’ve also attended enough cryptography classes to know that the probability of deriving the private key by brute force, is just too low to even consider. 👎<br>
					Now you can see why these twelve words are quite expensive; considering today’s price of Ethereum, they total around <i>£1,000</i>. <br><br>
					The moral of the story is to take security into your own hands when entering the cryptocurrency domain. By design, there is no ‘reset password’ links provided by these protocols. If you want to be in total control of your funds, without trusting an intermediary, then make sure you’ve taken the correct measures to avoid the situation above.<br><br>

					Let’s say you find yourself in a similar situation, where you've lost your Jaxx backup phrase. The only difference is that you’ve still got the machine that physically stores the bits that make up your 12-words (e.g. Laptop with the Jaxx chrome browser extension). 
					Inspired by an article on <a class="link" href="https://vxlabs.com/2017/06/10/extracting-the-jaxx-12-word-wallet-backup-phrase/" target="_blank">vxlabs</a>, which highlights a vulnerability in Jaxx; I was able to recover my current backup phrase, without having direct access to it via the wallet GUI i.e. didn't know Jaxx pin code.<br><br>

					In short, this is how:<br><br>

					For this tutorial, I created an empty Jaxx wallet to keep my own seed phrase a secret. I'm using MacOS with a Jaxx Blockchain Wallet (Verson  1.3.4.5) installed as a Google Chrome (Version 61.0.3163.100) extension.
					<br><br>
					After downloading and creating your pin protected Jaxx wallet, take note of your 12-word backup phrase. You’ll need this to see if you’ve successfully extracted the phrase from your filesystem at the end of the tutorial. The phrase that was generated for me was, <i>‘ghost marble error capable seminar around multiply owner click amused prevent fee’</i>. We will want to extract the exact same mnemonic/phrase to prove that you can bypass the wallets pin code.
					<br><br>
					To start, navigate to Chromes Local Storage folder. On MacOS Sierra it is, ‘/Users/[username]/Library/Application\ Support/Google/Chrome/Default/Local\ Storage/’. This folder holds user data for various extensions installed within Chrome. The folder will be named similar to “chrome-extension_ancbofgphhmhcchnaognahmjfajaecmo_0”. You can open this folder with sqlite3, which can be downloaded here. 
					<br><br>
					<p class="code">
						brew cask install db-browser-for-sqlite
					</p>
					<br><br>
					Once sqlite3 has successfully opened the file, run the following command over the storage:<br>
					<p class="code">
						select value<br> from ItemTable<br> where key="mnemonic";
					</p>
					<br>
					This should return a long string which is the encrypted 12-word phrase. If you can’t find the Local Storage folder or are having trouble retrieving the mnemonic, you can install the <a class="link" href="https://chrome.google.com/webstore/detail/storage-area-explorer/ocfjjjjhkpapocigimmppepjgfdecjkb?hl=en" target="_blank">Storage Area Explorer</a> extension in Google Chrome. Right click on the Jaxx wallet and select “Inspect Pop-up”. Navigate to the “Storage Explorer” tab and choose window.localStorage. You can copy the mnemonic from the array of data there. Alternatively you can simply type, <span class="code">window.localStorage.mnemonic</span> in the Chrome console.
					<br><br>

					<p class="code">
						> window.localStorage.mnemonic <br>
						> fotQ+ffgUXP59/qBVR6h5pXFw61
							NMUopq6rkXI6DrMw22Bu60P3V
							fTceDkDBpaO0yffFiUqdgcWDHH
							mUFMoPy9Fj1DDgCYwjZcD1pL/H
							A06dx9+qAkYd4Gk4K60//HGf<br>
					</p>
					<br><br>
					Note down the returned value for the next step. Using the following code, we will substitute our value from above into the mnemonicEncrypted value. Before executing this script, ensure you have Node.js and Crypto-js installed: <span class="code">npm install crypto-js@3.1.2</span>.
					<br><br>
					Save the file below as <i>generateSeedPhrase.js</i> and then execute it in the Node.js runtime.
					<br><br>
					<p class="code">
						/* <br>Jaxx recovery phrase extraction by<br> cpbotha@vxlabs.com 2017<br>
						vxlabs.com/2017/06/10/extracting-the-jaxx-12-word-wallet-backup-phrase/<br>
						You need v3.1.2 (same as latest jaxx) else you'll get invalid UTF-8 error<br>
						*/<br>
						var CryptoJS = require('crypto-js');<br>
						var _key = "6Le0DgMTAAAAANokdfEial";<br>
						var _iv  = "mHGFxENnZLbienLyALoi.e";<br><br>

						var mnemonicEncrypted=<br>"<span style="color: red">
						fotQ+ffgUXP59/qBVR6h5pXFw61NMU<br>
						opq6rkXI6DrMw22Bu60P3VfTceDkDB<br>paO0yffFiUqdgcWDHHmUFMoPy9Fj1D<br>DgCYwjZcD1pL/HA06dx9+qAkYd4Gk4K60//HGf</span>";<br><br>
						var _keyB;<br>
						var _ivB;<br><br>

						// js/vault/vault.js<br>
						function decryptSimple(encryptedTxt) {<br>
						    <span style="margin-left: 40px">_keyB = CryptoJS.enc.Base64.parse(_key);</span><br>
						    <span style="margin-left: 40px">_ivB = CryptoJS.enc.Base64.parse(_iv);</span><br>   
						    <span style="margin-left: 40px">var decrypted = CryptoJS.AES.decrypt(encryptedTxt, _keyB, { iv: _ivB });</span><br>
						    <span style="margin-left: 40px">var decryptedText = decrypted.toString(CryptoJS.enc.Utf8);</span><br>
						    <span style="margin-left: 40px">return decryptedText;</span><br>
						}<br><br>

						console.log(decryptSimple(mnemonicEncrypted));<br>
					</p><br><br>
					To run it refer to image below. Note that we've retrieved the 12-word phrase which will give us access to the Jaxx wallet, <i>'ghost marble error capable seminar around multiply owner click amused prevent fee'</i>. There are ways to protect yourself from this vulnerability which are discussed further <a class="link" href="https://vxlabs.com/2017/06/10/extracting-the-jaxx-12-word-wallet-backup-phrase/" target="_blank">here</a>.<br><br>

					<p class="code">
						> node generateSeedPhrase.js <br>
						> ghost marble error capable seminar around multiply owner click amused prevent fee
					</p>
					<br><br>
					Thanks,<br>
					Blaine

					<br><br>
					<b><i>** Disclaimer: </i></b><i>This is not financial advice.</i>
					<p></p>
						
				</div>
			</div>